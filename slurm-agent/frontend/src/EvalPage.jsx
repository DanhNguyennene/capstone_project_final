import { useState, useEffect, useRef, useCallback } from 'react'

const EVAL_URL = 'http://10.0.0.1:8080'

export default function EvalPage({ agentUrl }) {
  const [dataset, setDataset]     = useState([])
  const [results, setResults]     = useState({})
  const [metrics, setMetrics]     = useState(null)
  const [activeId, setActiveId]   = useState(null)
  const [detail, setDetail]       = useState(null) // { test, result }
  const [running, setRunning]     = useState(false)
  const [progress, setProgress]   = useState(0)
  const [filters, setFilters]     = useState({ scenario: '', category: '', status: '' })
  const [opts, setOpts]           = useState({ approve: true, judge: false, noVariants: false })
  const abortRef = useRef(null)
  const activeIdRef = useRef(activeId)
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

  const loadDefault = async () => {
    await fetch(`${EVAL_URL}/api/load-default-dataset`, { method: 'POST' })
    await refreshDataset()
  }

  const uploadFile = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    const fd = new FormData()
    fd.append('file', file)
    await fetch(`${EVAL_URL}/api/upload-dataset`, { method: 'POST', body: fd })
    e.target.value = ''
    await refreshDataset()
  }

  const loadTestDetail = async (id) => {
    setActiveId(id)
    const r = await fetch(`${EVAL_URL}/api/test/${id}`)
    const d = await r.json()
    setDetail(d)
  }

  // ── Run all via SSE ──────────────────────────────────────────

  const runAll = async () => {
    const ctrl = new AbortController()
    abortRef.current = ctrl
    setRunning(true)
    setProgress(0)

    const p = new URLSearchParams({
      agent_url: agentUrl,
      auto_approve: opts.approve,
      use_judge: opts.judge,
      no_variants: opts.noVariants,
    })
    if (filters.scenario) p.set('scenario', filters.scenario)
    if (filters.category) p.set('category', filters.category)

    try {
      const resp = await fetch(`${EVAL_URL}/api/run?${p}`, {
        method: 'POST', signal: ctrl.signal,
      })
      const reader = resp.body.getReader()
      const decoder = new TextDecoder()
      let buf = ''

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
            if (evt === 'test_start') {
              setProgress((parsed.index / dataset.length) * 100)
              setDataset(prev => prev.map(t =>
                t.id === parsed.id ? { ...t, status: 'running' } : t))
            } else if (evt === 'test_done') {
              setResults(prev => ({ ...prev, [parsed.id]: parsed.result }))
              setDataset(prev => prev.map(t =>
                t.id === parsed.id ? { ...t, status: parsed.result.passed ? 'passed' : 'failed' } : t))
              setProgress(((parsed.index + 1) / dataset.length) * 100)
              // Use ref to get current activeId (not stale closure)
              if (activeIdRef.current === parsed.id) {
                setDetail(d => d ? { ...d, result: parsed.result } : d)
              }
            } else if (evt === 'complete') {
              setMetrics(parsed.metrics)
              setProgress(100)
            }
          } catch {}
        }
      }
    } catch (e) {
      if (e.name !== 'AbortError') console.error(e)
    }
    setRunning(false)
  }

  const runSingle = async (id) => {
    const p = new URLSearchParams({
      agent_url: agentUrl, auto_approve: opts.approve, use_judge: opts.judge,
    })
    const r = await fetch(`${EVAL_URL}/api/run-single/${id}?${p}`, { method: 'POST' })
    const d = await r.json()
    setResults(prev => ({ ...prev, [id]: d.result }))
    setDataset(prev => prev.map(t =>
      t.id === id ? { ...t, status: d.result.passed ? 'passed' : 'failed' } : t))
    if (d.metrics) setMetrics(d.metrics)
    if (activeId === id) setDetail(prev => prev ? { ...prev, result: d.result } : prev)
  }

  const stopEval = () => { abortRef.current?.abort(); setRunning(false) }

  const clearResults = async () => {
    await fetch(`${EVAL_URL}/api/clear-results`, { method: 'POST' })
    setResults({})
    setMetrics(null)
    setDetail(null)
    setActiveId(null)
    setProgress(0)
    setDataset(prev => prev.map(t => ({ ...t, status: 'untested' })))
  }

  // Refresh on filter change
  useEffect(() => { if (dataset.length > 0) refreshDataset() }, [refreshDataset])

  // Init — check if eval server has data already
  useEffect(() => {
    (async () => {
      try {
        const r = await fetch(`${EVAL_URL}/api/status`)
        const s = await r.json()
        if (s.dataset_loaded) {
          await refreshDataset()
          const rr = await fetch(`${EVAL_URL}/api/results`)
          const rd = await rr.json()
          const rm = {}
          for (const res of rd.results) rm[res.test_id] = res
          setResults(rm)
          if (rd.metrics?.n_tests) setMetrics(rd.metrics)
        }
      } catch {}
    })()
  }, []) // eslint-disable-line

  // ── Keyboard nav ─────────────────────────────────────────────

  useEffect(() => {
    const handler = (e) => {
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

  // ── Helpers ──────────────────────────────────────────────────

  const pct = (v) => Math.round((v || 0) * 100) + '%'
  const scenarios   = [...new Set(dataset.map(t => t.scenario))].sort()
  const categories  = [...new Set(dataset.map(t => t.category))].sort()
  const tested = dataset.filter(t => results[t.id])
  const passed = tested.filter(t => results[t.id]?.passed)
  const failed = tested.length - passed.length
  const untested = dataset.length - tested.length

  const filteredList = dataset.filter(t => {
    if (filters.status === 'passed')  return results[t.id]?.passed === true
    if (filters.status === 'failed')  return results[t.id]?.passed === false
    if (filters.status === 'untested') return !results[t.id]
    return true
  })

  // ── Render ───────────────────────────────────────────────────

  return (
    <div className="eval-page">
      {/* Left panel: controls + test list */}
      <div className="eval-sidebar">
        <div className="eval-header">
          <span className="eval-title">Evaluation</span>
          <div className="eval-stats">
            <span className="eval-stat">{dataset.length} tests</span>
            <span className="eval-stat eval-stat-pass">{passed.length} ✓</span>
            <span className="eval-stat eval-stat-fail">{failed} ✗</span>
            <span className="eval-stat">{untested} ○</span>
          </div>
        </div>

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
          {['passed', 'failed', 'untested'].map(s => (
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

        {/* Test list */}
        <div className="eval-list">
          {filteredList.map(t => {
            const r = results[t.id]
            const status = r ? (r.passed ? 'passed' : 'failed') : t.status
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

      {/* Right panel: detail + metrics */}
      <div className="eval-main">
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
                ...(metrics.avg_judge_score > 0 ? [['Judge', metrics.avg_judge_score]] : []),
              ].map(([label, val]) => (
                <div className="eval-metric" key={label}>
                  <div className={`eval-metric-val ${val >= 0.8 ? 'good' : val < 0.5 ? 'bad' : 'mid'}`}>
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
        /> : (
          <div className="eval-empty">
            <div className="eval-empty-icon">📋</div>
            <p>Select a test case from the list</p>
          </div>
        )}
      </div>
    </div>
  )
}

// ── Test detail sub-component ──────────────────────────────────────

function TestDetail({ test, result, dataset, activeId, onNav, onRun, pct }) {
  if (!test) return null
  const gt = test.ground_truth
  const idx = dataset.findIndex(t => t.id === test.id)
  const prevId = idx > 0 ? dataset[idx - 1].id : null
  const nextId = idx < dataset.length - 1 ? dataset[idx + 1].id : null

  const dims = [
    { key: 'tool_recall',    label: 'Tool Recall', w: '30%' },
    { key: 'routing_match',  label: 'Routing',     w: '25%' },
    { key: 'hitl_match',     label: 'HITL',        w: '25%' },
    { key: 'keyword_score',  label: 'Keywords',    w: '10%' },
    { key: 'state_match',    label: 'State',       w: '10%' },
  ]
  if (result?.judge_score > 0) dims.push({ key: 'judge_score', label: 'Judge', w: '15%' })

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

      {/* Scores */}
      {result && (
        <div className="eval-section">
          <h3 className="eval-section-title">Scores</h3>
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
              <Field label="Tools" value={gt.tools.map(t => <Tag key={t} text={t} />)} />
              <Field label="Handoff" value={gt.handoff ? 'Yes' : 'No'} />
              <Field label="HITL" value={gt.hitl ? 'Yes' : 'No'} />
              <Field label="Keywords" value={gt.keywords.map(k => <Tag key={k} text={k} />)} />
            </div>
            <div className="eval-compare-col">
              <h4>Actual</h4>
              <Field label="Tools" value={
                (result.agent_tools || []).length > 0
                  ? result.agent_tools.map(t => <Tag key={t} text={t}
                      miss={!new Set(gt.tools).has(t)} />)
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
      {result?.judge_score > 0 && (
        <div className="eval-section">
          <h3 className="eval-section-title">LLM Judge</h3>
          <div className="eval-judge">
            <span className="eval-judge-score">{Math.round(result.judge_score * 4 + 1)}/5 ({pct(result.judge_score)})</span>
            {result.judge_reason && <p className="eval-judge-reason">{result.judge_reason}</p>}
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
