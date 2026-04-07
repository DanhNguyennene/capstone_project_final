// components/ThinkingBlock.jsx
import { useEffect, useRef, useState } from 'react'

export default function ThinkingBlock({ text, isStreaming }) {
  const [open, setOpen] = useState(true)
  const prev = useRef(isStreaming)

  useEffect(() => {
    if (prev.current && !isStreaming) setOpen(false)
    prev.current = isStreaming
  }, [isStreaming])

  return (
    <div className={`thinking${open ? ' open' : ''}`}>
      <button className="thinking-toggle" onClick={() => setOpen(o => !o)}>
        <span className="chevron">{open ? '▼' : '▶'}</span>
        ⚙ Thinking
        {isStreaming && <span className="thinking-live"> …</span>}
      </button>
      {open && <pre className="thinking-body">{text}</pre>}
    </div>
  )
}
