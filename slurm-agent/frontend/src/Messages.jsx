// Messages.jsx — thin container: imports all rendering components.
import { useEffect, useRef } from 'react'

import UserMessage      from './components/UserMessage'
import AssistantMessage from './components/AssistantMessage'

const SUGGESTIONS = [
  'Show all running jobs',
  'Why is my job pending?',
  'Show cluster resource usage',
  'Generate a system health chart',
  'List failed jobs today',
  'Show GPU resource availability',
]

export default function Messages({ messages, onSuggestion, onAction }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  if (messages.length === 0) {
    return (
      <div className="messages-empty">
        <div className="empty-icon">🖥</div>
        <h2 className="empty-title">Slurm Agent</h2>
        <p className="empty-sub">
          Ask anything about your HPC cluster — job status, queue info, resources, troubleshooting.
        </p>
        <div className="suggestions">
          {SUGGESTIONS.map(s => (
            <button key={s} className="suggestion" onClick={() => onSuggestion(s)}>{s}</button>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="messages">
      {messages.map(m =>
        m.role === 'user'
          ? <UserMessage      key={m.id} content={m.content} />
          : <AssistantMessage key={m.id} msg={m} onAction={onAction} />
      )}
      <div ref={bottomRef} />
    </div>
  )
}

