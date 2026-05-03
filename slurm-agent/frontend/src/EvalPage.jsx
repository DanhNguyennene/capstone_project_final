import { useState, useEffect, useRef, useCallback } from 'react'

const evalHost = typeof window !== 'undefined' ? window.location.hostname : 'localhost'
const EVAL_URL = `http://${evalHost}:8080`
const LS_OPTS_KEY = 'evalPage.opts.v1'
const LS_FILTERS_KEY = 'evalPage.filters.v1'
const clampWorkers = value => Math.max(1, Math.min(8, Number(value) || 1))
const defaultOpts = { approve: true, judge: false, noVariants: false }

function isPlaceholderJudgeReason(reason) {
  const txt = (reason || '').trim()
  if (!txt) return true
  if (txt === '...' || txt === '…' || txt === '-' || txt === '--') return true
  const squashed = txt.replace(/[\s.,;:\-_!?/\\]+/g, '').toLowerCase()
  if (['na', 'none', 'null', 'tbd', 'unknown', 'noreason'].includes(squashed)) return true
  return squashed.length < 10
}

export default function EvalPage({
  agentUrl,
  mcpUrl,
  llmProvider,
  mainProvider = llmProvider,
  specialistProvider = llmProvider,
  judgeProvider = llmProvider,
  mainModel,
  specialistModel,
  judgeModel,
  openaiParallel = false,
  parallelWorkers = 1,
  onParallelWorkersChange = null,
  sidebarOpen = true,
  onToggleGlobalSidebar = null,
}) {
  const [dataset, setDataset]     = useState([])
  const [results, setResults]     = useState({})
  const [metrics, setMetrics]     = useState(null)
  const [activeId, setActiveId]   = useState(null)
  const [detail, setDetail]       = useState(null) // { test, result }
  const [running, setRunning]     = useState(false)
  const [progress, setProgress]   = useState(0)
  const [judgeRunning, setJudgeRunning]   = useState(false)
  const [judgeProgress, setJudgeProgress] = useState(0)
  const [judgeTotal, setJudgeTotal]       = useState(0)
  const [judgeCurrentId, setJudgeCurrentId] = useState('')
  const [terminalTestId, setTerminalTestId] = useState('')
  const [terminalHistory, setTerminalHistory] = useState([])
  const [terminalCommand, setTerminalCommand] = useState('')
  const [, setTerminalHistoryCursor] = useState(-1)
  const [terminalRunning, setTerminalRunning] = useState(false)
  const [filters, setFilters]     = useState(() => {
    try {
      const raw = localStorage.getItem(LS_FILTERS_KEY)
      if (raw) return { scenario: '', category: '', status: '', ...JSON.parse(raw) }
    } catch {}
    return { scenario: '', category: '', status: '' }
  })
  const [opts, setOpts]           = useState(() => {
    try {
      const raw = localStorage.getItem(LS_OPTS_KEY)
      if (raw) {
        const parsed = { ...defaultOpts, ...JSON.parse(raw) }
        return parsed
      }
    } catch {}
    return defaultOpts
  })
  const abortRef = useRef(null)
  const runTotalRef = useRef(0)
  const activeIdRef = useRef(activeId)
  const terminalInputRef = useRef(null)
  const terminalBodyRef = useRef(null)
  activeIdRef.current = activeId

  // ── Data loading ─────────────────────────────────────────────

  const refreshDataset = useCallback(async () => {
    const p = new URLSearchParams()
    if (filters.scenario) p.set('scenario', filters.scenario)
    if (filters.category) p.set('category', filters.category)
    if (opts.noVariants) p.set('no_variants', 'true')
    try {
      const r = await fetch(`${EVAL_URL}/api/dataset?${p}`)
      const d = await r.json()
      setDataset(d.tests)
    } catch { /* eval server not running */ }
  }, [filters.scenario, filters.category, opts.noVariants])

  const _syncResultsFromServer = async () => {
    const rr = await fetch(`${EVAL_URL}/api/results`)
    const rd = await rr.json()
    const rm = {}
    for (const res of (rd.results || [])) rm[res.test_id] = res
    setResults(rm)
    setMetrics(rd.metrics?.n_tests ? rd.metrics : null)
    setDetail(prev => {
      if (!prev?.test?.id) return prev
      return { ...prev, result: rm[prev.test.id] || null }
    })
  }

  const loadDefault = async () => {
    await fetch(`${EVAL_URL}/api/load-default-dataset`, { method: 'POST' })
    await refreshDataset()
    await _syncResultsFromServer()   // bring back preserved results
  }

  const uploadFile = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    const fd = new FormData()
    fd.append('file', file)
    await fetch(`${EVAL_URL}/api/upload-dataset`, { method: 'POST', body: fd })
    e.target.value = ''
    await refreshDataset()
    await _syncResultsFromServer()
  }

  const refreshTerminalHistory = useCallback(async (testId = '') => {
    const p = new URLSearchParams()
    if (testId) p.set('test_id', testId)
    try {
      const r = await fetch(`${EVAL_URL}/api/terminal/history?${p.toString()}`)
      const d = await r.json()
      setTerminalHistory(Array.isArray(d.history) ? d.history : [])
    } catch {
      setTerminalHistory([])
    }
  }, [])

  const loadTestDetail = async (id) => {
    setActiveId(id)
    try {
      await refreshTerminalHistory(id)
      const rr = await fetch(`${EVAL_URL}/api/test/${id}`)
      const d = await rr.json()
      setDetail(d)
    } catch {
      // no-op
    }
  }

  const runTerminalCommand = async () => {
    const contextId = terminalTestId || activeId || ''
    const cmd = terminalCommand.trim()
    if (!cmd || !contextId) return
    setTerminalRunning(true)
    try {
      const r = await fetch(`${EVAL_URL}/api/terminal/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: cmd, test_id: contextId, mcp_url: mcpUrl }),
      })
      let d = {}
      try {
        d = await r.json()
      } catch {
        d = {}
      }
      if (Array.isArray(d.history)) {
        setTerminalHistory(d.history)
      } else {
        const fallbackError = !r.ok
          ? `Terminal request failed (HTTP ${r.status})`
          : 'Terminal response malformed.'
        const errorText = (typeof d.error === 'string' && d.error.trim()) ? d.error : fallbackError
        setTerminalHistory(prev => ([
          ...prev,
          {
            id: Date.now(),
            prompt: 'slurm@hpc:~$ ',
            command: cmd,
            output: errorText,
            ok: false,
          },
        ]))
      }
      if (r.ok) {
        setTerminalCommand('')
        setTerminalHistoryCursor(-1)
      }
    } catch (err) {
      const msg = (err && err.message) ? err.message : 'Could not reach eval server.'
      setTerminalHistory(prev => ([
        ...prev,
        {
          id: Date.now(),
          prompt: 'slurm@hpc:~$ ',
          command: cmd,
          output: `Network error: ${msg}`,
          ok: false,
        },
      ]))
    } finally {
      setTerminalRunning(false)
    }
  }

  const clearTerminalHistory = async () => {
    const contextId = terminalTestId || activeId || ''
    if (!contextId) return
    try {
      await fetch(`${EVAL_URL}/api/terminal/clear`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ test_id: contextId }),
      })
      setTerminalHistory([])
    } catch {
      // No-op
    }
  }

  const markBadTestCase = async () => {
    const contextId = terminalTestId || activeId || ''
    if (!contextId) return
    try {
      const r = await fetch(`${EVAL_URL}/api/test/${encodeURIComponent(contextId)}/mark-bad`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason: 'Manually flagged by admin terminal.' }),
      })
      const d = await r.json().catch(() => ({}))
      if (r.ok && d?.result) {
        setResults(prev => ({ ...prev, [contextId]: d.result }))
        if (d.metrics) setMetrics(d.metrics)
        setDetail(prev => {
          if (!prev?.test?.id || prev.test.id !== contextId) return prev
          return { ...prev, result: d.result }
        })
      }
    } catch {
      // No-op
    }
  }

  // ── Run all via SSE ──────────────────────────────────────────

  const consumeRunStream = useCallback(async (resp, totalHint = 0) => {
    if (!resp?.ok || !resp.body) return
    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buf = ''
    runTotalRef.current = totalHint || runTotalRef.current || 0

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buf += decoder.decode(value, { stream: true })

      while (true) {
        const end = buf.indexOf('\n\n')
        if (end === -1) break
        const frame = buf.slice(0, end)
        buf = buf.slice(end + 2)

        let evt = '', data = ''
        for (const ln of frame.split('\n')) {
          if (ln.startsWith('event: ')) evt = ln.slice(7)
          else if (ln.startsWith('data: ')) data = ln.slice(6)
        }
        if (!data) continue
        try {
          const parsed = JSON.parse(data)
          if (evt === 'start') {
            if (typeof parsed.total === 'number') runTotalRef.current = parsed.total
            if (typeof parsed.judge_total === 'number') setJudgeTotal(parsed.judge_total)
            setJudgeProgress(0)
            setJudgeCurrentId('')
            setJudgeRunning(false)
            if (typeof parsed.already_done === 'number') {
              const denom = runTotalRef.current || dataset.length || 1
              setProgress((parsed.already_done / denom) * 100)
            }
          } else if (evt === 'test_start') {
            const denom = runTotalRef.current || dataset.length || 1
            const completed = (typeof parsed.completed === 'number') ? parsed.completed : parsed.index
            setProgress((completed / denom) * 100)
            setDataset(prev => prev.map(t =>
              t.id === parsed.id ? { ...t, status: 'running' } : t))
          } else if (evt === 'test_done') {
            setResults(prev => ({ ...prev, [parsed.id]: parsed.result }))
            setDataset(prev => prev.map(t =>
              t.id === parsed.id
                ? { ...t, status: parsed.result.judge_pending ? 'judging' : (parsed.result.passed ? 'passed' : 'failed') }
                : t))
            const denom = runTotalRef.current || dataset.length || 1
            const completed = (typeof parsed.completed === 'number')
              ? parsed.completed
              : (typeof parsed.index === 'number' ? parsed.index + 1 : 0)
            setProgress((completed / denom) * 100)
            if (activeIdRef.current === parsed.id) {
              setDetail(d => d ? { ...d, result: parsed.result } : d)
            }
          } else if (evt === 'judge_start') {
            setJudgeRunning(true)
            setJudgeProgress(0)
            if (typeof parsed.total === 'number') setJudgeTotal(parsed.total)
          } else if (evt === 'judge_test_start') {
            setJudgeCurrentId(parsed.id || '')
            setDataset(prev => prev.map(t =>
              t.id === parsed.id ? { ...t, status: 'judging' } : t))
          } else if (evt === 'judge_done') {
            setJudgeProgress(typeof parsed.done === 'number' ? parsed.done : 0)
            setResults(prev => ({ ...prev, [parsed.id]: parsed.result }))
            setDataset(prev => prev.map(t =>
              t.id === parsed.id ? { ...t, status: parsed.result.passed ? 'passed' : 'failed' } : t))
            if (activeIdRef.current === parsed.id) {
              setDetail(d => d ? { ...d, result: parsed.result } : d)
            }
          } else if (evt === 'judge_complete') {
            setJudgeRunning(false)
            setJudgeCurrentId('')
            setJudgeProgress(prev => (typeof parsed.done === 'number' ? parsed.done : prev))
          } else if (evt === 'complete') {
            setMetrics(parsed.metrics)
            setProgress(100)
            setJudgeRunning(false)
            setJudgeCurrentId('')
            setRunning(false)
          } else if (evt === 'stopped' || evt === 'error') {
            setJudgeRunning(false)
            setJudgeCurrentId('')
            setRunning(false)
          }
        } catch {}
      }
    }
  }, [dataset.length])

  const runAll = async () => {
    if (running) return
    const ctrl = new AbortController()
    abortRef.current = ctrl
    setRunning(true)
    setProgress(0)
    setJudgeRunning(false)
    setJudgeProgress(0)
    setJudgeCurrentId('')
    setJudgeTotal(opts.judge ? dataset.length : 0)

    const p = new URLSearchParams({
      agent_url: agentUrl,
      mcp_url: mcpUrl,
      auto_approve: opts.approve,
      use_judge: opts.judge,
      judge_model: judgeModel,
      judge_provider: judgeProvider,
      llm_provider: llmProvider,
      main_provider: mainProvider,
      specialist_provider: specialistProvider,
      main_model: mainModel,
      specialist_model: specialistModel,
      openai_parallel: openaiParallel,
      parallel_workers: clampWorkers(parallelWorkers),
      no_variants: opts.noVariants,
      resume: 'true',
    })
    if (filters.scenario) p.set('scenario', filters.scenario)
    if (filters.category) p.set('category', filters.category)

    try {
      let resp = await fetch(`${EVAL_URL}/api/run?${p}`, {
        method: 'POST', signal: ctrl.signal,
      })
      // If server thinks a run is already active (stale state), force-reset and retry once
      if (resp.status === 409) {
        await fetch(`${EVAL_URL}/api/stop`, { method: 'POST' })
        p.set('force', 'true')
        resp = await fetch(`${EVAL_URL}/api/run?${p}`, {
          method: 'POST', signal: ctrl.signal,
        })
      }
      await consumeRunStream(resp, dataset.length)
    } catch (e) {
      if (e.name !== 'AbortError') console.error(e)
    }
    setRunning(false)
  }

  const runSingle = async (id) => {
    const p = new URLSearchParams({
      agent_url: agentUrl,
      mcp_url: mcpUrl,
      auto_approve: opts.approve,
      use_judge: opts.judge,
      judge_model: judgeModel,
      judge_provider: judgeProvider,
      llm_provider: llmProvider,
      main_provider: mainProvider,
      specialist_provider: specialistProvider,
      main_model: mainModel,
      specialist_model: specialistModel,
      openai_parallel: openaiParallel,
    })
    const r = await fetch(`${EVAL_URL}/api/run-single/${id}?${p}`, { method: 'POST' })
    const d = await r.json()
    setResults(prev => ({ ...prev, [id]: d.result }))
    setDataset(prev => prev.map(t =>
      t.id === id ? { ...t, status: d.result.passed ? 'passed' : 'failed' } : t))
    if (d.metrics) setMetrics(d.metrics)
    if (activeId === id) setDetail(prev => prev ? { ...prev, result: d.result } : prev)
  }

  const stopEval = async () => {
    abortRef.current?.abort()
    setRunning(false)
    setJudgeRunning(false)
    setJudgeCurrentId('')
    try { await fetch(`${EVAL_URL}/api/stop`, { method: 'POST' }) } catch {}
  }

  const clearResults = async () => {
    await fetch(`${EVAL_URL}/api/clear-results`, { method: 'POST' })
    setResults({})
    setMetrics(null)
    setDetail(null)
    setActiveId(null)
    setProgress(0)
    setJudgeRunning(false)
    setJudgeProgress(0)
    setJudgeTotal(0)
    setJudgeCurrentId('')
    setTerminalTestId('')
    setTerminalCommand('')
    setTerminalHistoryCursor(-1)
    setTerminalHistory([])
    setDataset(prev => prev.map(t => ({ ...t, status: 'untested' })))
  }

  // Refresh on filter change
  useEffect(() => { if (dataset.length > 0) refreshDataset() }, [refreshDataset])

  // Persist UI selections so "ticks" survive reload/return.
  useEffect(() => {
    try { localStorage.setItem(LS_OPTS_KEY, JSON.stringify(opts)) } catch {}
  }, [opts])
  useEffect(() => {
    try { localStorage.setItem(LS_FILTERS_KEY, JSON.stringify(filters)) } catch {}
  }, [filters])

  // Init — check if eval server has data already
  useEffect(() => {
    (async () => {
      try {
        const r = await fetch(`${EVAL_URL}/api/status`)
        const s = await r.json()
        runTotalRef.current = s.total || 0
        setRunning(!!s.running)
        setJudgeRunning(!!s.judge_running)
        setJudgeProgress(s.judge_progress || 0)
        setJudgeTotal(s.judge_total || 0)
        if (!s.judge_running) setJudgeCurrentId('')
        if (s.running && s.model_config?.parallel_workers) onParallelWorkersChange?.(s.model_config.parallel_workers)
        if (typeof s.progress === 'number' && (s.total || 0) > 0) {
          setProgress((s.progress / s.total) * 100)
        }
        if (s.dataset_loaded) {
          await refreshDataset()
          const rr = await fetch(`${EVAL_URL}/api/results`)
          const rd = await rr.json()
          const rm = {}
          for (const res of rd.results) rm[res.test_id] = res
          setResults(rm)
          if (rd.metrics?.n_tests) setMetrics(rd.metrics)
        }
        await refreshTerminalHistory(activeIdRef.current || '')

        // If a run is still active when user returns, re-attach stream so UI
        // continues updating live without restarting the run.
        if (s.running) {
          const p = new URLSearchParams({
            agent_url: agentUrl,
            mcp_url: mcpUrl,
            auto_approve: opts.approve,
            use_judge: opts.judge,
            judge_model: judgeModel,
            judge_provider: judgeProvider,
            llm_provider: llmProvider,
            main_provider: mainProvider,
            specialist_provider: specialistProvider,
            main_model: mainModel,
            specialist_model: specialistModel,
            openai_parallel: openaiParallel,
            parallel_workers: clampWorkers(parallelWorkers),
            no_variants: opts.noVariants,
            resume: 'true',
          })
          if (filters.scenario) p.set('scenario', filters.scenario)
          if (filters.category) p.set('category', filters.category)
          const attachResp = await fetch(`${EVAL_URL}/api/run?${p}`, { method: 'POST' })
          await consumeRunStream(attachResp, s.total || dataset.length)
        }
      } catch {}
    })()
  }, [agentUrl, mcpUrl, llmProvider, mainProvider, specialistProvider, judgeProvider, mainModel, specialistModel, judgeModel, openaiParallel, parallelWorkers, onParallelWorkersChange, opts.approve, opts.judge, opts.noVariants, filters.scenario, filters.category, refreshDataset, consumeRunStream, refreshTerminalHistory])

  // ── Keyboard nav ─────────────────────────────────────────────

  useEffect(() => {
    const handler = (e) => {
      const target = e.target
      const tag = (target?.tagName || '').toLowerCase()
      if (tag === 'input' || tag === 'textarea' || tag === 'select' || target?.isContentEditable) return
      if (e.metaKey || e.ctrlKey || e.altKey) return
      if (!activeId || !dataset.length) return
      const idx = dataset.findIndex(t => t.id === activeId)
      if ((e.key === 'ArrowDown' || e.key === 'j') && idx < dataset.length - 1) {
        e.preventDefault(); loadTestDetail(dataset[idx + 1].id)
      }
      if ((e.key === 'ArrowUp' || e.key === 'k') && idx > 0) {
        e.preventDefault(); loadTestDetail(dataset[idx - 1].id)
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [activeId, dataset])

  useEffect(() => {
    if (activeId && terminalTestId !== activeId) {
      setTerminalTestId(activeId)
      setTerminalHistoryCursor(-1)
      refreshTerminalHistory(activeId)
      return
    }
    if (!dataset.length) {
      if (terminalTestId) setTerminalTestId('')
      setTerminalHistoryCursor(-1)
      setTerminalHistory([])
      return
    }
    const stillValid = terminalTestId && dataset.some(t => t.id === terminalTestId)
    if (!stillValid) {
      const first = dataset[0].id
      setTerminalTestId(first)
      setTerminalHistoryCursor(-1)
      refreshTerminalHistory(first)
    }
  }, [activeId, dataset, terminalTestId, refreshTerminalHistory])

  useEffect(() => {
    const el = terminalBodyRef.current
    if (el) el.scrollTop = el.scrollHeight
  }, [terminalHistory, activeId, terminalRunning])

  // ── Helpers ──────────────────────────────────────────────────

  const pct = (v) => Math.round((v || 0) * 100) + '%'
  const scenarios   = [...new Set(dataset.map(t => t.scenario))].sort()
  const categories  = [...new Set(dataset.map(t => t.category))].sort()
  const tested = dataset.filter(t => results[t.id] && !results[t.id]?.judge_pending)
  const pendingJudge = dataset.filter(t => results[t.id]?.judge_pending).length
  const passed = tested.filter(t => results[t.id]?.passed)
  const failed = tested.length - passed.length
  const untested = dataset.length - tested.length - pendingJudge

  const filteredList = dataset.filter(t => {
    if (filters.status === 'passed')  return results[t.id]?.judge_pending !== true && results[t.id]?.passed === true
    if (filters.status === 'failed')  return results[t.id]?.judge_pending !== true && results[t.id]?.passed === false
    if (filters.status === 'judging') return results[t.id]?.judge_pending === true || t.status === 'judging'
    if (filters.status === 'untested') return !results[t.id]
    return true
  })
  const terminalCommandHistory = terminalHistory
    .map(entry => (entry?.command || '').trim())
    .filter(Boolean)

  // ── Render ───────────────────────────────────────────────────

  return (
    <div className="eval-page">
      {onToggleGlobalSidebar && (
        <button
          className="eval-global-sidebar-toggle"
          onClick={onToggleGlobalSidebar}
          title={sidebarOpen ? 'Hide app sidebar' : 'Show app sidebar'}
        >
          {sidebarOpen ? '⟨' : '⟩'}
        </button>
      )}
      {/* Left panel: controls + test list */}
      <div className="eval-sidebar">
        <div className="eval-header">
          <div className="eval-header-row">
            <span className="eval-title">Evaluation</span>
          </div>
          <div className="eval-stats">
            <span className="eval-stat">{dataset.length} tests</span>
            <span className="eval-stat eval-stat-pass">{passed.length} ✓</span>
            <span className="eval-stat eval-stat-fail">{failed} ✗</span>
            <span className="eval-stat">{pendingJudge} …</span>
            <span className="eval-stat">{untested} ○</span>
          </div>
        </div>

        <div className="eval-sidebar-body">
        {/* Controls */}
        <div className="eval-controls">
          <div className="eval-ctrl-row">
            <button className="eval-btn eval-btn-primary" onClick={loadDefault}>Load Dataset</button>
            <label className="eval-btn eval-btn-ghost" style={{ cursor: 'pointer' }}>
              Upload <input type="file" accept=".json" style={{ display: 'none' }} onChange={uploadFile} />
            </label>
          </div>
          <div className="eval-ctrl-row">
            <label className="eval-check">
              <input type="checkbox" checked={opts.approve} onChange={e => setOpts(o => ({ ...o, approve: e.target.checked }))} />
              Auto-approve
            </label>
            <label className="eval-check">
              <input type="checkbox" checked={opts.judge} onChange={e => setOpts(o => ({ ...o, judge: e.target.checked }))} />
              Judge
            </label>
            <label className="eval-check">
              <input type="checkbox" checked={opts.noVariants} onChange={e => setOpts(o => ({ ...o, noVariants: e.target.checked }))} />
              No variants
            </label>
            <label className="eval-check">
              Eval workers
              <input
                className="eval-worker-input"
                type="number"
                min="1"
                max="8"
                value={parallelWorkers}
                onChange={e => onParallelWorkersChange?.(e.target.value)}
              />
            </label>
          </div>
          {opts.judge && (
            <div className="eval-ctrl-row">
              <span className="eval-check">Judge model: {judgeModel}</span>
            </div>
          )}
          <div className="eval-ctrl-row">
            <span className="eval-check">Eval model: {llmProvider} / {mainModel}</span>
          </div>
          <div className="eval-ctrl-row">
            <button className="eval-btn eval-btn-run" onClick={runAll} disabled={running || !dataset.length}>
              ▶ Run All
            </button>
            <button className="eval-btn eval-btn-stop" onClick={stopEval} disabled={!running}>
              ■ Stop
            </button>
            <button className="eval-btn eval-btn-ghost eval-btn-sm" onClick={clearResults} disabled={running || Object.keys(results).length === 0}
              title="Clear all results">
              ✕ Clear
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="eval-filters">
          {scenarios.map(s => (
            <span key={s}
              className={`eval-chip${filters.scenario === s ? ' active' : ''}`}
              onClick={() => setFilters(f => ({ ...f, scenario: f.scenario === s ? '' : s }))}
            >{s}</span>
          ))}
          {categories.map(c => (
            <span key={c}
              className={`eval-chip${filters.category === c ? ' active' : ''}`}
              onClick={() => setFilters(f => ({ ...f, category: f.category === c ? '' : c }))}
            >{c}</span>
          ))}
          {['passed', 'failed', 'judging', 'untested'].map(s => (
            <span key={s}
              className={`eval-chip eval-chip-${s}${filters.status === s ? ' active' : ''}`}
              onClick={() => setFilters(f => ({ ...f, status: f.status === s ? '' : s }))}
            >{s}</span>
          ))}
        </div>

        {/* Progress */}
        {running && (
          <div className="eval-progress">
            <div className="eval-progress-fill" style={{ width: `${progress}%` }} />
          </div>
        )}
        {judgeRunning && (
          <div className="eval-judge-loading">
            LLM is judging… {judgeProgress}/{judgeTotal || '?'}{judgeCurrentId ? ` · ${judgeCurrentId}` : ''}
          </div>
        )}

        {/* Test list */}
        <div className="eval-list">
          {filteredList.map(t => {
            const r = results[t.id]
            let status = t.status || 'untested'
            if (status !== 'running') {
              if (r?.judge_pending) status = 'judging'
              else if (r) status = r.passed ? 'passed' : 'failed'
            }
            return (
              <div
                key={t.id}
                className={`eval-item${activeId === t.id ? ' active' : ''}`}
                onClick={() => loadTestDetail(t.id)}
              >
                <span className={`eval-dot eval-dot-${status}`} />
                <div className="eval-item-info">
                  <div className="eval-item-id">
                    {t.id}
                    {t.is_variant && <span className="eval-variant-tag">v</span>}
                    {r?.bad_test_case && <span className="eval-badcase-tag">bad-case</span>}
                  </div>
                  <div className="eval-item-meta">{t.category} · {t.scenario}</div>
                </div>
                {r && (
                  <span className={`eval-item-score ${r.passed ? 'pass' : 'fail'}`}>
                    {pct(r.overall)}
                  </span>
                )}
              </div>
            )
          })}
          {dataset.length === 0 && (
            <div className="eval-empty-list">Load a dataset to begin</div>
            )}
        </div>
          </div>
      </div>

      {/* Right panel: detail + metrics + admin terminal */}
      <div className="eval-main">
        <div className="eval-main-layout">
          <div className="eval-main-content">
            {/* Metrics bar — always on top when available */}
            {metrics && (
              <div className="eval-metrics">
                <h3 className="eval-section-title">Results Summary</h3>
                <div className="eval-metrics-grid">
                  {[
                    ['Pass', metrics.pass_rate],
                    ['BAR', metrics.BAR],
                    ['SVR', metrics.SVR],
                    ['CSR', metrics.CSR],
                    ['Tool↻', metrics.avg_tool_recall],
                    ['Route', metrics.avg_routing_match],
                    ['HITL', metrics.avg_hitl_match],
                    ['Overall', metrics.avg_overall],
                    ['BadTC', metrics.bad_test_case_rate, true],
                    ...(metrics.avg_judge_score != null && opts.judge ? [['Judge', metrics.avg_judge_score]] : []),
                  ].map(([label, val, invertGood]) => (
                    <div className="eval-metric" key={label}>
                      <div className={`eval-metric-val ${
                        invertGood
                          ? (val <= 0.05 ? 'good' : val >= 0.2 ? 'bad' : 'mid')
                          : (val >= 0.8 ? 'good' : val < 0.5 ? 'bad' : 'mid')
                      }`}>
                        {pct(val)}
                      </div>
                      <div className="eval-metric-label">{label}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Detail view */}
            {detail ? <TestDetail
              test={detail.test}
              result={detail.result || results[detail.test?.id]}
              dataset={dataset}
              activeId={activeId}
              onNav={loadTestDetail}
              onRun={runSingle}
              pct={pct}
              judgeEnabled={opts.judge}
            /> : (
              <div className="eval-empty">
                <div className="eval-empty-icon">📋</div>
                <p>Select a test case from the list</p>
              </div>
            )}
          </div>

          <aside className="eval-admin-sidebar">
            <div className="eval-admin-head">
              <div>
                <h3 className="eval-section-title" style={{ marginBottom: 2 }}>Human Eval Terminal</h3>
                <div className="eval-admin-sub">
                  {terminalTestId
                    ? `Context: ${terminalTestId} (isolated per test)`
                    : 'Select a test to start terminal'}
                </div>
                <div className="eval-admin-sub">On smaller screens this panel moves below the detail view.</div>
              </div>
              <select
                className="eval-admin-select"
                value={terminalTestId}
                onChange={e => {
                  const next = e.target.value
                  setTerminalTestId(next)
                  setTerminalHistoryCursor(-1)
                  refreshTerminalHistory(next)
                }}
                disabled={dataset.length === 0 || terminalRunning}
                title="Select terminal context test"
              >
                {dataset.map(t => <option key={t.id} value={t.id}>{t.id}</option>)}
              </select>
              <button
                className="eval-btn eval-btn-ghost eval-btn-sm"
                onClick={clearTerminalHistory}
                disabled={!terminalTestId || terminalHistory.length === 0 || terminalRunning}
              >
                Clear
              </button>
              <button
                className="eval-btn eval-btn-ghost eval-btn-sm"
                onClick={markBadTestCase}
                disabled={!terminalTestId || terminalRunning}
                title="Flag this test as an invalid/bad test case"
              >
                ⚑ Flag Bad
              </button>
            </div>

            <div className="eval-terminal eval-admin-terminal">
              <div className="eval-terminal-bar">
                <span className="eval-terminal-dot" style={{ background: '#ff5f56' }} />
                <span className="eval-terminal-dot" style={{ background: '#ffbd2e' }} />
                <span className="eval-terminal-dot" style={{ background: '#27c93f' }} />
                <span className="eval-terminal-title">slurm@hpc admin shell</span>
              </div>
              <div
                className="eval-terminal-body"
                ref={terminalBodyRef}
                onClick={() => terminalInputRef.current?.focus()}
              >
                {terminalHistory.length === 0 ? (
                  <span className="eval-term-empty">
                    {terminalTestId
                      ? 'No commands yet for this test. Start with: squeue'
                      : 'Select a test to open an isolated terminal session'}
                  </span>
                ) : terminalHistory.map((entry, i) => (
                  <div key={entry.id || `${entry.command}-${i}`} className="eval-term-block">
                    <div className="eval-term-cmdline">
                      <span className="eval-term-ps1">{entry.prompt || 'slurm@hpc:~$ '}</span>
                      <span className={`eval-term-cmd${entry.ok === false ? ' eval-term-cmd-extra' : ''}`}>
                        {entry.command}
                      </span>
                    </div>
                    <pre className="eval-term-output">{entry.output || '(no output)'}</pre>
                  </div>
                ))}
                {terminalRunning && (
                  <div className="eval-term-sys">Running command…</div>
                )}
              </div>
            </div>

            <div className="eval-admin-input-row">
              <span className="eval-term-ps1">slurm@hpc:~$&nbsp;</span>
              <input
                ref={terminalInputRef}
                className="eval-admin-input"
                value={terminalCommand}
                onChange={e => {
                  setTerminalCommand(e.target.value)
                  setTerminalHistoryCursor(-1)
                }}
                onKeyDown={e => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    e.stopPropagation()
                    runTerminalCommand()
                    return
                  }
                  if (e.key === 'ArrowUp') {
                    e.preventDefault()
                    e.stopPropagation()
                    if (!terminalCommandHistory.length) return
                    setTerminalHistoryCursor(prev => {
                      const next = prev < 0
                        ? terminalCommandHistory.length - 1
                        : Math.max(0, prev - 1)
                      setTerminalCommand(terminalCommandHistory[next] || '')
                      return next
                    })
                    return
                  }
                  if (e.key === 'ArrowDown') {
                    e.preventDefault()
                    e.stopPropagation()
                    if (!terminalCommandHistory.length) return
                    setTerminalHistoryCursor(prev => {
                      if (prev < 0) return -1
                      const next = prev + 1
                      if (next >= terminalCommandHistory.length) {
                        setTerminalCommand('')
                        return -1
                      }
                      setTerminalCommand(terminalCommandHistory[next] || '')
                      return next
                    })
                  }
                }}
                placeholder="squeue --state PENDING"
                disabled={!terminalTestId || terminalRunning}
              />
              <button
                className="eval-btn eval-btn-primary eval-btn-sm"
                onClick={runTerminalCommand}
                disabled={!terminalTestId || terminalRunning || !terminalCommand.trim()}
              >
                Run
              </button>
            </div>
            <div className="eval-admin-hint">
              Commands are persisted per test and state is restored per context. Use ↑/↓ for command history.
            </div>
          </aside>
        </div>
      </div>
    </div>
  )
}

// ── Test detail sub-component ──────────────────────────────────────

const TOOL_ALIASES = {
  sacctmgr_list: 'sacctmgr_show',
  sacctmgr: 'sacctmgr_show',
  scontrol: 'scontrol_show',
}

const TOOL_EQUIVALENTS = {
  sacctmgr_show: ['sacctmgr_show', 'sacctmgr_list'],
  sacctmgr_list: ['sacctmgr_show', 'sacctmgr_list'],
}

function normalizeToolName(tool) {
  return TOOL_ALIASES[tool] || tool
}

function equivalentToolNames(tool, aliasMap = null) {
  const canonical = normalizeToolName(tool)
  if (aliasMap?.[canonical]?.length) return aliasMap[canonical]
  if (aliasMap?.[tool]?.length) return aliasMap[tool]
  return TOOL_EQUIVALENTS[canonical] || [canonical]
}

function acceptedToolSet(tools = [], aliasMap = null) {
  const accepted = new Set()
  tools.forEach(tool => {
    equivalentToolNames(tool, aliasMap).forEach(name => accepted.add(name))
    accepted.add(normalizeToolName(tool))
  })
  return accepted
}

function historyToolName(entry) {
  if (entry.tool) return entry.tool
  const tokens = (entry.cmd || '').replace(/^\$ /, '').trim().split(/\s+/).filter(Boolean)
  if (tokens[0] === 'sacctmgr' && ['show', 'list'].includes(tokens[1])) return 'sacctmgr_list'
  return tokens[0] || ''
}

function toolIsExpected(tool, expectedSet = null, aliasMap = null) {
  if (!expectedSet) return false
  if (expectedSet.has(tool) || expectedSet.has(normalizeToolName(tool))) return true
  return equivalentToolNames(tool, aliasMap).some(name => expectedSet.has(name) || expectedSet.has(normalizeToolName(name)))
}

function ToolTagList({ tools = [], aliasMap = null, expectedSet = null }) {
  const canonicalTools = [...new Set(tools.map(normalizeToolName))]
  if (canonicalTools.length === 0) return <span className="text-muted">none</span>
  return (
    <TagList>
      {canonicalTools.map(tool => (
        <Tag
          key={tool}
          text={equivalentToolNames(tool, aliasMap).join(' / ')}
          miss={expectedSet ? !toolIsExpected(tool, expectedSet, aliasMap) : false}
        />
      ))}
    </TagList>
  )
}

function TagList({ children }) {
  return <span className="eval-tag-list">{children}</span>
}

function TestDetail({ test, result, dataset, activeId, onNav, onRun, pct, judgeEnabled }) {
  if (!test) return null
  const gt = test.ground_truth
  const resultAliasMap = result?.gt_tool_aliases || null
  const expectedTools = (result?.gt_tools_canonical?.length ? result.gt_tools_canonical : (gt.tools || []))
  const expectedToolSet = acceptedToolSet(expectedTools, resultAliasMap)
  const idx = dataset.findIndex(t => t.id === test.id)
  const prevId = idx > 0 ? dataset[idx - 1].id : null
  const nextId = idx < dataset.length - 1 ? dataset[idx + 1].id : null

  const judgePending = result?.judge_pending === true
  // judge ran only when backend says so; fallback supports older result files.
  const judgeRan = !judgePending && ((result?.judge_ran === true) || (!!result?.judge_reason))
  const rawJudgeReason = (result?.judge_reason || '').trim()
  const hasConcreteJudgeReason = !!rawJudgeReason && !isPlaceholderJudgeReason(rawJudgeReason)
  const judgeReasonText = hasConcreteJudgeReason
    ? rawJudgeReason
    : (
      (result?.error || '').trim()
      || 'Judge output was low-quality/placeholder. Please rerun this test with Judge enabled.'
    )

  const dims = judgeRan
    ? [
      { key: 'tool_recall',    label: 'Tool Recall', w: '25%' },
      { key: 'routing_match',  label: 'Routing',     w: '20%' },
      { key: 'hitl_match',     label: 'HITL',        w: '20%' },
      { key: 'keyword_score',  label: 'Keywords',    w: '10%' },
      { key: 'state_match',    label: 'State',       w: '10%' },
      { key: 'judge_score',    label: 'Judge',       w: '15%' },
    ]
    : [
      { key: 'tool_recall',    label: 'Tool Recall', w: '30%' },
      { key: 'routing_match',  label: 'Routing',     w: '25%' },
      { key: 'hitl_match',     label: 'HITL',        w: '25%' },
      { key: 'keyword_score',  label: 'Keywords',    w: '10%' },
      { key: 'state_match',    label: 'State',       w: '10%' },
    ]

  // State transitions
  const src = test.source_state?.jobs || {}
  const tgt = test.target_state?.jobs || {}
  const changed = Object.keys(src).filter(jid => tgt[jid] && src[jid].state !== tgt[jid].state)

  return (
    <div className="eval-detail">
      <div className="eval-detail-head">
        <h2>{test.id}</h2>
        <span className="eval-detail-meta">
          {test.category} · {test.scenario}
          {test.variant_of && ` (variant of ${test.variant_of})`}
        </span>
      </div>

      <div className="eval-prompt">{test.input}</div>

      {result?.bad_test_case && (
        <div className="eval-section">
          <h3 className="eval-section-title">Test Case Quality</h3>
          <div className="eval-badcase-panel">
            <div className="eval-badcase-title">⚠ Flagged as potentially invalid test case</div>
            <div className="eval-badcase-reason">
              {(result.bad_test_case_reason || 'No reason provided by evaluator.').trim()}
            </div>
          </div>
        </div>
      )}

      {/* Scores */}
      {result && (
        <div className="eval-section">
          <h3 className="eval-section-title">Scores (Selected Test)</h3>
          <div className="eval-scores">
            {dims.map(d => {
              const v = result[d.key] ?? 0
              return (
                <div key={d.key} className={`eval-score-card ${v >= 0.99 ? 'pass' : v < 0.5 ? 'fail' : ''}`}>
                  <div className={`eval-score-val ${v >= 0.99 ? 'good' : v < 0.5 ? 'bad' : 'mid'}`}>
                    {pct(v)}
                  </div>
                  <div className="eval-score-label">{d.label} ({d.w})</div>
                </div>
              )
            })}
            <div className={`eval-score-card overall ${result.passed ? 'pass' : 'fail'}`}>
              <div className={`eval-score-val ${result.passed ? 'good' : 'bad'}`}>
                {pct(result.overall)}
              </div>
              <div className="eval-score-label">Overall {result.passed ? '✓' : '✗'}</div>
            </div>
          </div>
        </div>
      )}

      {/* GT vs Agent */}
      {result && (
        <div className="eval-section">
          <h3 className="eval-section-title">Ground Truth vs Agent</h3>
          <div className="eval-compare">
            <div className="eval-compare-col">
              <h4>Expected</h4>
              <Field label="Tools" value={<ToolTagList tools={expectedTools} aliasMap={resultAliasMap} />} />
              <Field label="Handoff" value={gt.handoff ? 'Yes' : 'No'} />
              <Field label="HITL" value={gt.hitl ? 'Yes' : 'No'} />
              <Field label="Keywords" value={<TagList>{(gt.keywords || []).map(k => <Tag key={k} text={k} />)}</TagList>} />
            </div>
            <div className="eval-compare-col">
              <h4>Actual</h4>
              <Field label="Tools" value={
                (result.agent_tools || []).length > 0
                  ? <ToolTagList tools={result.agent_tools} aliasMap={resultAliasMap} expectedSet={expectedToolSet} />
                  : <span className="text-muted">none</span>
              } />
              <Field label="Handoff" value={
                <span className={result.agent_handoff === gt.handoff ? 'eval-match' : 'eval-mismatch'}>
                  {result.agent_handoff ? 'Yes' : 'No'} {result.agent_handoff === gt.handoff ? '✓' : '✗'}
                </span>
              } />
              <Field label="HITL" value={
                <span className={result.agent_hitl === gt.hitl ? 'eval-match' : 'eval-mismatch'}>
                  {result.agent_hitl ? 'Yes' : 'No'} {result.agent_hitl === gt.hitl ? '✓' : '✗'}
                </span>
              } />
              <Field label="Latency" value={`${result.latency_s}s`} />
            </div>
          </div>
        </div>
      )}

      {/* Tool Call History */}
      {result && (
        <div className="eval-section">
          <h3 className="eval-section-title">Tool Call History</h3>
          <div className="eval-terminal">
            <div className="eval-terminal-bar">
              <span className="eval-terminal-dot" style={{background:'#ff5f56'}}/>
              <span className="eval-terminal-dot" style={{background:'#ffbd2e'}}/>
              <span className="eval-terminal-dot" style={{background:'#27c93f'}}/>
              <span className="eval-terminal-title">slurm-mcp-agent — bash</span>
            </div>
            <div className="eval-terminal-body">
              {(() => {
                const history = result.tool_call_history || [];
                if (history.length === 0 && (!result.agent_tools || result.agent_tools.length === 0)) {
                  return <span className="eval-term-empty">No tool calls recorded for this test</span>;
                }
                const lines = history.length > 0
                  ? history
                  : result.agent_tools.map((t, i) => ({ type: 'tool', cmd: `$ ${t}`, tool: t, index: i }));

                return lines.map((entry, i) => {
                  const cmd = entry.cmd || '';
                  if (entry.type === 'tool') {
                    const toolName = historyToolName(entry);
                    const isExtra  = !toolIsExpected(toolName, expectedToolSet, resultAliasMap);
                    const cmdBody  = cmd.replace(/^\$ /, '');
                    return (
                      <div key={i} className="eval-term-block">
                        <div className="eval-term-cmdline">
                          <span className="eval-term-ps1">slurm@hpc:~$&nbsp;</span>
                          <span className={`eval-term-cmd${isExtra ? ' eval-term-cmd-extra' : ''}`}>{cmdBody}</span>
                          {isExtra
                            ? <span className="eval-term-annotation eval-term-extra">&nbsp;&nbsp;# unexpected</span>
                            : <span className="eval-term-annotation eval-term-ok">&nbsp;&nbsp;# ✓ expected</span>}
                        </div>
                        {entry.output && (
                          <pre className="eval-term-output">{entry.output}</pre>
                        )}
                      </div>
                    );
                  }
                  if (entry.type === 'handoff') {
                    return (
                      <div key={i} className="eval-term-sys">
                        <span className="eval-term-sys-icon">↪</span>
                        {cmd}
                      </div>
                    );
                  }
                  if (entry.type === 'approved') {
                    return (
                      <div key={i} className="eval-term-sys eval-term-sys-ok">
                        {cmd}
                      </div>
                    );
                  }
                  if (entry.type === 'retry') {
                    return (
                      <div key={i} className="eval-term-sys eval-term-sys-warn">
                        {cmd}
                      </div>
                    );
                  }
                  /* type === 'result' — old summary line, skip (output now on tool entry) */
                  return null;
                });
              })()}
              <div className="eval-term-cmdline eval-term-idle">
                <span className="eval-term-ps1">slurm@hpc:~$&nbsp;</span>
                <span className="eval-term-cursor">█</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* State transitions */}
      <div className="eval-section">
        <h3 className="eval-section-title">State Transition</h3>
        {changed.length > 0 ? (
          <div className="eval-state-changes">
            {changed.map(jid => (
              <Tag key={jid} text={`${jid}: ${src[jid].state} → ${tgt[jid].state}`} />
            ))}
          </div>
        ) : (
          <span className="text-muted" style={{ fontSize: 12 }}>No state change expected (read-only)</span>
        )}
      </div>

      {/* Judge */}
      {judgeEnabled && judgePending && (
        <div className="eval-section">
          <h3 className="eval-section-title">LLM Judge</h3>
          <div className="eval-judge eval-judge-pending">
            <span className="eval-judge-score eval-judge-error">LLM is judging…</span>
          </div>
        </div>
      )}

      {judgeRan && (
        <div className="eval-section">
          <h3 className="eval-section-title">LLM Judge</h3>
          <div className="eval-judge">
            <div className="eval-judge-header">
              {(result && typeof result.judge_score === 'number')
                ? <span className="eval-judge-score">{Math.round(result.judge_score * 4 + 1)}/5 ({pct(result.judge_score)})</span>
                : <span className="eval-judge-score eval-judge-error">Score unavailable</span>
              }
            </div>
            {hasConcreteJudgeReason
              ? <pre className="eval-judge-text">{rawJudgeReason}</pre>
              : <p className="eval-judge-reason" style={{ fontStyle: 'italic' }}>{judgeReasonText}</p>
            }
          </div>
        </div>
      )}

      {/* Thinking */}
      {result?.agent_thinking && (
        <div className="eval-section">
          <h3 className="eval-section-title">Agent Thinking</h3>
          <pre className="eval-response eval-thinking">{result.agent_thinking}</pre>
        </div>
      )}

      {/* Response */}
      {result && (
        <div className="eval-section">
          <h3 className="eval-section-title">Agent Response</h3>
          <pre className="eval-response">{result.agent_response || '(empty)'}</pre>
        </div>
      )}

      {/* Error */}
      {result?.error && (
        <div className="eval-section">
          <h3 className="eval-section-title">Error</h3>
          <pre className="eval-response eval-response-err">{result.error}</pre>
        </div>
      )}

      {/* Actions */}
      <div className="eval-actions">
        <button className="eval-btn eval-btn-primary eval-btn-sm" onClick={() => onRun(test.id)}>
          ▶ Run
        </button>
      </div>

      {/* Navigation */}
      <div className="eval-nav">
        <button className="eval-btn eval-btn-ghost eval-btn-sm" disabled={!prevId}
          onClick={() => prevId && onNav(prevId)}>← Prev</button>
        <span className="text-muted" style={{ fontSize: 11 }}>{idx + 1} / {dataset.length}</span>
        <button className="eval-btn eval-btn-ghost eval-btn-sm" disabled={!nextId}
          onClick={() => nextId && onNav(nextId)}>Next →</button>
      </div>
    </div>
  )
}

function Field({ label, value }) {
  return (
    <div className="eval-field">
      <div className="eval-field-label">{label}</div>
      <div className="eval-field-value">{value}</div>
    </div>
  )
}

function Tag({ text, miss }) {
  return <span className={`eval-tag${miss ? ' miss' : ''}`}>{text}</span>
}
