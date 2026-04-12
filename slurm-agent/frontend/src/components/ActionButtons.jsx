// components/ActionButtons.jsx
// Shown when the agent has queued a dangerous action and awaits user confirmation.

function summarize(action) {
  const desc = action.description || action.tool || ''
  // For sbatch/scancel with comma-separated args, show count instead of full list
  const m = desc.match(/^(\w+)\((.+)\)$/)
  if (m) {
    const [, tool, inner] = m
    const paths = inner.split(',')
    if (paths.length > 2) {
      const key = inner.split('=')[0] // e.g., "script" or "job_id"
      return `${tool}(${key}: ${paths.length} items)`
    }
  }
  // Truncate long single-item descriptions
  return desc.length > 80 ? desc.slice(0, 77) + '…' : desc
}

export default function ActionButtons({ actions, onAction }) {
  if (!actions?.length) return null
  return (
    <div className="action-row">
      <span className="action-label">⚠️ Awaiting confirmation:</span>
      <div className="action-btns">
        {actions.map((a, i) => (
          <span key={i} className="action-item" title={a.description || a.tool}>
            {summarize(a)}
          </span>
        ))}
        <button className="action-confirm" onClick={() => onAction('approve')}>
          ✓ Confirm
        </button>
        <button className="action-cancel" onClick={() => onAction('reject')}>
          × Cancel
        </button>
      </div>
    </div>
  )
}
