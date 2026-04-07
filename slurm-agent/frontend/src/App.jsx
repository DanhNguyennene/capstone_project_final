import { useEffect, useRef, useState } from 'react'
import Sidebar  from './Sidebar'
import Messages from './Messages'
import InputBar from './InputBar'
import { checkHealth } from './api'
import { URL_KEY }     from './lib/storage'
import { useSessions } from './hooks/useSessions'
import { useStream }   from './hooks/useStream'

export default function App() {
  const [agentUrl,    setAgentUrl]    = useState(() => localStorage.getItem(URL_KEY) || 'http://localhost:8000')
  const [streaming,   setStreaming]   = useState(false)
  const [status,      setStatus]      = useState({ state: 'idle', text: 'Connecting…' })
  const [sidebarOpen, setSidebarOpen] = useState(true)

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
    agentUrl, activeIdRef, setSessions, setStreaming, setStatus, patchMsg, createSession,
  })

  // Bootstrap: ensure at least one session exists
  useEffect(() => {
    if (!activeId || !sessions[activeId]) createSession()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Ping agent on URL change
  useEffect(() => {
    localStorage.setItem(URL_KEY, agentUrl)
    checkHealth(agentUrl)
      .then(ok => setStatus(ok ? { state: 'online', text: 'Ready' } : { state: 'offline', text: 'Unreachable' }))
      .catch(() => setStatus({ state: 'offline', text: 'Disconnected' }))
  }, [agentUrl])

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
        />

        <InputBar onSend={sendMessage} disabled={streaming} onStop={() => abortRef.current?.abort()} />
      </div>
    </div>
  )
}

