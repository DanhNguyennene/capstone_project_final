export default function Sidebar({
  open, sessions, activeId, onNew, onSelect, onDelete, agentUrl, onUrlChange,
}) {
  return (
    <nav className={`sidebar${open ? '' : ' collapsed'}`}>
      <div className="sidebar-brand">
        <span className="brand-icon">🖥</span>
        <span className="brand-name"><strong>Slurm</strong> Agent</span>
      </div>

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

      <div className="sidebar-footer">
        <label className="footer-label">Agent URL</label>
        <input
          className="url-input"
          type="text"
          value={agentUrl}
          onChange={e => onUrlChange(e.target.value)}
          placeholder="http://localhost:8000"
          spellCheck={false}
        />
      </div>
    </nav>
  )
}
