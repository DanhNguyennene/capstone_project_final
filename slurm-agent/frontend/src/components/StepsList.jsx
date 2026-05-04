// components/StepsList.jsx
// Copilot-style tool-trace list shown inside assistant messages.
// Completed steps are faded with a green ✓; the active step has a spinner.
// Tool outputs are rendered as collapsible terminal blocks.

import { useState } from 'react'

export default function StepsList({ steps, isStreaming }) {
  if (!steps?.length) return null
  return (
    <div className="steps-list">
      {steps.map((step, i) => {
        // Support both legacy string format and new object format
        const item = typeof step === 'string' ? { type: 'step', text: step } : step

        if (item.type === 'output') {
          return <ToolOutput key={i} text={item.text} />
        }

        const isActive = isStreaming && i === steps.length - 1
        return (
          <div key={i} className={`step ${isActive ? 'step-active' : 'step-done'}`}>
            {isActive
              ? <span className="step-spinner" />
              : <span className="step-check">✓</span>}
            <span className="step-text">{item.text}</span>
          </div>
        )
      })}
    </div>
  )
}

function ToolOutput({ text }) {
  const [expanded, setExpanded] = useState(false)
  const lines = text.split('\n')
  const preview = lines.slice(0, 2).join('\n')
  const hasMore = lines.length > 2

  return (
    <div className="step-tool-output">
      <pre className="step-tool-output-pre">
        {expanded ? text : preview}
      </pre>
      {hasMore && (
        <button
          className="step-tool-output-toggle"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? '▲ Collapse' : `▼ Show all (${lines.length} lines)`}
        </button>
      )}
    </div>
  )
}
