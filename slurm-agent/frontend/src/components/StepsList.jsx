// components/StepsList.jsx
// Copilot-style tool-trace list shown inside assistant messages.
// Completed steps are faded with a green ✓; the active step has a spinner.

export default function StepsList({ steps, isStreaming }) {
  if (!steps?.length) return null
  return (
    <div className="steps-list">
      {steps.map((step, i) => {
        const isActive = isStreaming && i === steps.length - 1
        return (
          <div key={i} className={`step ${isActive ? 'step-active' : 'step-done'}`}>
            {isActive
              ? <span className="step-spinner" />
              : <span className="step-check">✓</span>}
            <span className="step-text">{step}</span>
          </div>
        )
      })}
    </div>
  )
}
