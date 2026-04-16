export default function Sidebar({
  open, sessions, activeId, onNew, onSelect, onDelete, mcpUrl, onMcpUrlChange,
  view, onViewChange,
}) {
  return (
    <nav className={`sidebar${open ? '' : ' collapsed'}`}>
      <div className="sidebar-brand">
        <span className="brand-icon">🖥</span>
        <span className="brand-name"><strong>Slurm</strong> Agent</span>
      </div>

      {/* View toggle */}
      <div className="view-toggle">
        <button className={`view-tab${view === 'chat' ? ' active' : ''}`} onClick={() => onViewChange('chat')}>
          💬 Chat
        </button>
        <button className={`view-tab${view === 'eval' ? ' active' : ''}`} onClick={() => onViewChange('eval')}>
          📋 Eval
        </button>
      </div>

      {view === 'chat' && (
        <>
          <button className="new-chat-btn" onClick={onNew}>
            <span>＋</span> New Chat
          </button>

          <div className="section-label">Sessions</div>

          <div className="sessions-list">
            {sessions.length === 0 && (
              <p className="sessions-empty">No sessions yet.</p>
            )}
            {sessions.map(s => (
              <div
                key={s.id}
                className={`session-item${s.id === activeId ? ' active' : ''}`}
                onClick={() => onSelect(s.id)}
              >
                <span className="session-icon">💬</span>
                <span className="session-name" title={s.title}>{s.title}</span>
                <button
                  className="session-del"
                  title="Delete session"
                  onClick={e => { e.stopPropagation(); onDelete(s.id) }}
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        </>
      )}

      {view === 'eval' && (
        <div className="eval-sidebar-info">
          <div className="section-label">Evaluation</div>
          <p className="sessions-empty">
            Run tests against the live agent and inspect results in real time.
          </p>
        </div>
      )}

      <div className="sidebar-footer">
        <label className="footer-label">MCP Server</label>
        <input
          className="url-input"
          type="text"
          value={mcpUrl}
          onChange={e => onMcpUrlChange(e.target.value)}
          placeholder="http://localhost:3002"
          spellCheck={false}
        />
      </div>
    </nav>
  )
}
