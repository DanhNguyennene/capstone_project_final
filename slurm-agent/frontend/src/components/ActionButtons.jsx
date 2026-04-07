// components/ActionButtons.jsx
// Shown when the agent has queued a dangerous action and awaits user confirmation.

export default function ActionButtons({ actions, onAction }) {
  if (!actions?.length) return null
  return (
    <div className="action-row">
      <span className="action-label">⚠️ Awaiting confirmation:</span>
      <div className="action-btns">
        {actions.map((a, i) => (
          <span key={i} className="action-item">{a.description || a.tool}</span>
        ))}
        <button className="action-confirm" onClick={() => onAction('yes')}>
          ✓ Confirm
        </button>
        <button className="action-cancel" onClick={() => onAction('cancel')}>
          × Cancel
        </button>
      </div>
    </div>
  )
}
