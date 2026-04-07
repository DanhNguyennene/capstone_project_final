import { useState, useEffect, useRef } from 'react'
import Sidebar from './Sidebar'
import Messages from './Messages'
import InputBar from './InputBar'
import { streamChat, checkHealth, clearSessionOnServer } from './api'

// ── Storage helpers ────────────────────────────────────────────────
const SESSIONS_KEY = 'slurm_sessions_v2'
const ACTIVE_KEY   = 'slurm_active_v2'
const URL_KEY      = 'slurm_url'

function loadSessions() {
  try { return JSON.parse(localStorage.getItem(SESSIONS_KEY) || '{}') }
  catch { return {} }
}

function mkId() {
  return 'sess_' + Date.now() + '_' + Math.random().toString(36).slice(2, 6)
}

function mkMsg(role, content = '') {
  return {
    id: Date.now() + Math.random(),
    role,
    content,
    thinking: '',
    statusText: '',
    webResults: [],
    streaming: false,
    pendingActions: [],
  }
}

// ── App ────────────────────────────────────────────────────────────
export default function App() {
  const [sessions,    setSessions]    = useState(() => loadSessions())
  const [activeId,    setActiveId]    = useState(() => localStorage.getItem(ACTIVE_KEY))
  const [agentUrl,    setAgentUrl]    = useState(() => localStorage.getItem(URL_KEY) || 'http://localhost:8000')
  const [streaming,   setStreaming]   = useState(false)
  const [status,      setStatus]      = useState({ state: 'idle', text: 'Connecting…' })
  const [sidebarOpen, setSidebarOpen] = useState(true)

  // sid ref so async callbacks always see latest value
  const activeIdRef = useRef(activeId)
  activeIdRef.current = activeId

  // abort controller for cancelling in-flight stream
  const abortRef = useRef(null)

  // ── Bootstrap ──────────────────────────────────────────────────
  useEffect(() => {
    if (!activeId || !loadSessions()[activeId]) createSession()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => { localStorage.setItem(SESSIONS_KEY, JSON.stringify(sessions)) }, [sessions])
  useEffect(() => { if (activeId) localStorage.setItem(ACTIVE_KEY, activeId) }, [activeId])
  useEffect(() => {
    localStorage.setItem(URL_KEY, agentUrl)
    checkHealth(agentUrl)
      .then(ok => setStatus(ok ? { state: 'online', text: 'Ready' } : { state: 'offline', text: 'Unreachable' }))
      .catch(() => setStatus({ state: 'offline', text: 'Disconnected' }))
  }, [agentUrl])

  // ── Session management ─────────────────────────────────────────
  function createSession() {
    const id = mkId()
    setSessions(prev => ({ ...prev, [id]: { id, title: 'New Chat', messages: [], created: Date.now() } }))
    setActiveId(id)
    return id
  }

  function selectSession(id) {
    setActiveId(id)
  }

  function deleteSession(id) {
    setSessions(prev => {
      const next = { ...prev }
      delete next[id]
      return next
    })
    if (activeId === id) {
      const remaining = Object.keys(sessions).filter(k => k !== id)
      remaining.length > 0 ? setActiveId(remaining[0]) : createSession()
    }
  }

  async function clearSession() {
    if (!activeIdRef.current) return
    if (!confirm('Clear this chat?')) return
    const id = activeIdRef.current
    setSessions(prev => ({
      ...prev,
      [id]: { ...prev[id], messages: [], title: 'New Chat' },
    }))
    clearSessionOnServer(agentUrl, id).catch(() => {})
  }

  // ── Send message ───────────────────────────────────────────────
  async function sendMessage(text) {
    if (!text.trim() || streaming) return

    let sid = activeIdRef.current
    if (!sid || !loadSessions()[sid]) sid = createSession()

    // Auto-title first message
    const isFirst = (loadSessions()[sid]?.messages?.length ?? 0) === 0
    const title = isFirst ? text.slice(0, 44) + (text.length > 44 ? '…' : '') : undefined

    const userMsg = mkMsg('user', text)
    const asstMsg = { ...mkMsg('assistant'), streaming: true }

    setSessions(prev => {
      const s = prev[sid] || { id: sid, title: 'New Chat', messages: [], created: Date.now() }
      return {
        ...prev,
        [sid]: {
          ...s,
          ...(title ? { title } : {}),
          messages: [...s.messages, userMsg, asstMsg],
        },
      }
    })

    setStreaming(true)
    setStatus({ state: 'thinking', text: 'Thinking…' })

    const controller = new AbortController()
    abortRef.current = controller

    try {
      let thinking = ''
      let content  = ''
      // Whether we're currently inside a <think> block mid-stream
      let inThink  = false

      for await (const delta of streamChat(agentUrl, sid, text, controller.signal)) {
        // Actual model reasoning (gemma4: delta.reasoning, qwen3: delta.reasoning_content)
        if (delta.reasoning_content || delta.reasoning)
          thinking += delta.reasoning_content ?? delta.reasoning
        // Status updates (tool calls, agent switches) — separate from reasoning
        if (delta.status_update) {
          patchMsg(sid, asstMsg.id, { statusText: delta.status_update })
        }
        if (delta.pending_actions) {
          // Store pending actions so buttons render on this message
          patchMsg(sid, asstMsg.id, { pendingActions: delta.pending_actions })
        }
        if (delta.content) {
          // Route <think>...</think> segments into the thinking field
          let chunk = delta.content
          let processed = ''
          while (chunk.length > 0) {
            if (inThink) {
              const end = chunk.indexOf('</think>')
              if (end === -1) { thinking += chunk; chunk = '' }
              else { thinking += chunk.slice(0, end); chunk = chunk.slice(end + 8); inThink = false }
            } else {
              const start = chunk.indexOf('<think>')
              if (start === -1) { processed += chunk; chunk = '' }
              else { processed += chunk.slice(0, start); chunk = chunk.slice(start + 7); inThink = true }
            }
          }
          content += processed
        }

        setSessions(prev => {
          const s = prev[sid]
          if (!s) return prev
          return {
            ...prev,
            [sid]: {
              ...s,
              messages: s.messages.map(m =>
                m.id === asstMsg.id ? { ...m, thinking, content } : m
              ),
            },
          }
        })
      }
    } catch (err) {
      if (err.name === 'AbortError') {
        patchMsg(sid, asstMsg.id, { streaming: false })
        setStatus({ state: 'online', text: 'Ready' })
      } else {
        patchMsg(sid, asstMsg.id, { content: `⚠ ${err.message}`, streaming: false })
        setStatus({ state: 'offline', text: 'Error' })
      }
      setStreaming(false)
      return
    }

    patchMsg(sid, asstMsg.id, { streaming: false })
    setStreaming(false)
    setStatus({ state: 'online', text: 'Ready' })
  }

  // Called from the confirm/cancel buttons rendered by Messages
  function handleAction(actionText) {
    sendMessage(actionText)
  }

  function patchMsg(sid, msgId, patch) {
    setSessions(prev => {
      const s = prev[sid]
      if (!s) return prev
      return {
        ...prev,
        [sid]: {
          ...s,
          messages: s.messages.map(m => m.id === msgId ? { ...m, ...patch } : m),
        },
      }
    })
  }

  // ── Render ─────────────────────────────────────────────────────
  const sessionList    = Object.values(sessions).sort((a, b) => b.created - a.created)
  const currentSession = sessions[activeId]

  return (
    <div className="app">
      <Sidebar
        open={sidebarOpen}
        sessions={sessionList}
        activeId={activeId}
        onNew={createSession}
        onSelect={selectSession}
        onDelete={deleteSession}
        agentUrl={agentUrl}
        onUrlChange={setAgentUrl}
      />

      <div className="main">
        <header className="topbar">
          <button className="icon-btn" onClick={() => setSidebarOpen(o => !o)} title="Toggle sidebar">
            ☰
          </button>
          <span className="topbar-title">{currentSession?.title || 'New Chat'}</span>
          <div className="status-group">
            <span className={`dot dot-${status.state}`} />
            <span className="status-label">{status.text}</span>
          </div>
          <button className="ghost-btn" onClick={clearSession}>Clear</button>
        </header>

        <Messages
          messages={currentSession?.messages || []}
          onSuggestion={sendMessage}
          onAction={handleAction}
        />

        <InputBar onSend={sendMessage} disabled={streaming} onStop={() => abortRef.current?.abort()} />
      </div>
    </div>
  )
}
