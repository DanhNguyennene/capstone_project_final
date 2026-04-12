import { useEffect, useRef, useState } from 'react'
import Sidebar  from './Sidebar'
import Messages from './Messages'
import InputBar from './InputBar'
import TodoList from './components/TodoList'
import { checkHealth } from './api'
import { URL_KEY, MCP_URL_KEY } from './lib/storage'
import { useSessions } from './hooks/useSessions'
import { useStream }   from './hooks/useStream'

export default function App() {
  const [agentUrl]    = useState(() => localStorage.getItem(URL_KEY) || 'http://localhost:8000')
  const [mcpUrl,      setMcpUrl]      = useState(() => localStorage.getItem(MCP_URL_KEY) || 'http://localhost:3002')
  const [streaming,   setStreaming]   = useState(false)
  const [status,      setStatus]      = useState({ state: 'idle', text: 'Connecting…' })
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [todoList,    setTodoList]    = useState([])  // session-level plan

  const {
    sessions, setSessions, activeId, setActiveId,
    sessionList, currentSession,
    createSession, selectSession, deleteSession, clearSession,
    patchMsg,
  } = useSessions()

  // Stable ref so async stream callbacks always see the latest activeId
  const activeIdRef  = useRef(activeId)
  activeIdRef.current = activeId

  const { sendMessage, handleAction, abortRef } = useStream({
    agentUrl, mcpUrl, activeIdRef, setSessions, setStreaming, setStatus, patchMsg, createSession,
    onTodoUpdate: setTodoList,
  })

  // Clear plan when switching sessions
  useEffect(() => { setTodoList([]) }, [activeId])

  // Bootstrap: ensure at least one session exists
  useEffect(() => {
    if (!activeId || !sessions[activeId]) createSession()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Ping agent on URL change
  useEffect(() => {
    localStorage.setItem(URL_KEY, agentUrl)
    localStorage.setItem(MCP_URL_KEY, mcpUrl)
    checkHealth(agentUrl)
      .then(ok => setStatus(ok ? { state: 'online', text: 'Ready' } : { state: 'offline', text: 'Unreachable' }))
      .catch(() => setStatus({ state: 'offline', text: 'Disconnected' }))
  }, [agentUrl, mcpUrl])

  return (
    <div className="app">
      <Sidebar
        open={sidebarOpen}
        sessions={sessionList}
        activeId={activeId}
        onNew={createSession}
        onSelect={selectSession}
        onDelete={deleteSession}
        mcpUrl={mcpUrl}
        onMcpUrlChange={setMcpUrl}
      />

      <div className="main">
        <header className="topbar">
          <button className="icon-btn" onClick={() => setSidebarOpen(o => !o)} title="Toggle sidebar">☰</button>
          <span className="topbar-title">{currentSession?.title || 'New Chat'}</span>
          <div className="status-group">
            <span className={`dot dot-${status.state}`} />
            <span className="status-label">{status.text}</span>
          </div>
          <button className="ghost-btn" onClick={() => clearSession(agentUrl, activeId)}>Clear</button>
        </header>

        <Messages
          messages={currentSession?.messages || []}
          onSuggestion={sendMessage}
          onAction={handleAction}
          todoList={todoList}
        />

        <InputBar onSend={sendMessage} disabled={streaming} onStop={() => abortRef.current?.abort()} agentUrl={agentUrl} />
      </div>
    </div>
  )
}

