export default function Sidebar({
  open, sessions, activeId, onNew, onSelect, onDelete,
  agentUrl, onAgentUrlChange,
  mcpUrl, onMcpUrlChange,
  mainProvider,
  specialistProvider,
  judgeProvider,
  onMainProviderChange,
  onSpecialistProviderChange,
  onJudgeProviderChange,
  mainModel,
  specialistModel,
  judgeModel,
  mainModelOptions = [],
  specialistModelOptions = [],
  judgeModelOptions = [],
  onMainModelChange,
  onSpecialistModelChange,
  onJudgeModelChange,
  openaiParallel = false,
  onOpenaiParallelChange,
  parallelWorkers = 1,
  onParallelWorkersChange,
  view, onViewChange,
}) {
  const optionsFor = (value, options) => (
    options.includes(value)
      ? options
      : [value, ...options]
  )

  const providerSelect = (value, onChange) => (
    <select
      className="url-input provider-select"
      value={value}
      onChange={e => onChange(e.target.value)}
    >
      <option value="ollama">Ollama</option>
      <option value="openai">OpenAI</option>
      <option value="azure-openai">Azure OpenAI</option>
      <option value="finetuned">Finetuned (LoRA)</option>
    </select>
  )

  return (
    <nav className={`sidebar${open ? '' : ' collapsed'}${view === 'eval' ? ' sidebar-eval-mode' : ''}`}>
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
        <label className="footer-label">Agent API</label>
        <input
          className="url-input"
          type="text"
          value={agentUrl}
          onChange={e => onAgentUrlChange(e.target.value)}
          placeholder="http://localhost:8000"
          spellCheck={false}
        />

        <label className="footer-label">MCP Server</label>
        <input
          className="url-input"
          type="text"
          value={mcpUrl}
          onChange={e => onMcpUrlChange(e.target.value)}
          placeholder="http://localhost:3002"
          spellCheck={false}
        />

        <label className="footer-label">Main Provider</label>
        {providerSelect(mainProvider, onMainProviderChange)}

        <label className="footer-label">Main Model</label>
        <select
          className="url-input provider-select"
          value={mainModel}
          onChange={e => onMainModelChange(e.target.value)}
        >
          {optionsFor(mainModel, mainModelOptions).map(model => (
            <option key={model} value={model}>{model}</option>
          ))}
        </select>

        <label className="footer-label">Specialist Provider</label>
        {providerSelect(specialistProvider, onSpecialistProviderChange)}

        <label className="footer-label">Specialist Model</label>
        <select
          className="url-input provider-select"
          value={specialistModel}
          onChange={e => onSpecialistModelChange(e.target.value)}
        >
          {optionsFor(specialistModel, specialistModelOptions).map(model => (
            <option key={model} value={model}>{model}</option>
          ))}
        </select>

        <label className="footer-label">Judge Provider</label>
        {providerSelect(judgeProvider, onJudgeProviderChange)}

        <label className="footer-label">Judge Model</label>
        <select
          className="url-input provider-select"
          value={judgeModel}
          onChange={e => onJudgeModelChange(e.target.value)}
        >
          {optionsFor(judgeModel, judgeModelOptions).map(model => (
            <option key={model} value={model}>{model}</option>
          ))}
        </select>

        <label className={`footer-toggle${mainProvider !== 'openai' ? ' disabled' : ''}`}>
          <input
            type="checkbox"
            checked={openaiParallel && mainProvider === 'openai'}
            disabled={mainProvider !== 'openai'}
            onChange={e => onOpenaiParallelChange?.(e.target.checked)}
          />
          OpenAI read parallel
        </label>

        <label className="footer-label">Parallel Eval Workers</label>
        <input
          className="url-input worker-input"
          type="number"
          min="1"
          max="8"
          value={parallelWorkers}
          onChange={e => onParallelWorkersChange?.(e.target.value)}
        />

        <p className="footer-hint">
          Main and Specialist can use different providers. Azure OpenAI uses backend environment credentials, never browser-stored keys.
        </p>
      </div>
    </nav>
  )
}
