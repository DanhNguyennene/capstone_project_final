import { useRef } from 'react'

export default function InputBar({ onSend, disabled, onStop }) {
  const ref = useRef(null)

  function submit() {
    const text = ref.current?.value.trim()
    if (!text || disabled) return
    onSend(text)
    ref.current.value = ''
    ref.current.style.height = 'auto'
  }

  function handleKey(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  function autoResize() {
    const el = ref.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 180) + 'px'
  }

  return (
    <div className="input-area">
      <div className={`input-wrap${disabled ? ' input-wrap-disabled' : ''}`}>
        <textarea
          ref={ref}
          className="input-box"
          rows={1}
          placeholder={disabled ? 'Waiting for response…' : 'Ask about your cluster…'}
          onKeyDown={handleKey}
          onInput={autoResize}
          disabled={disabled}
        />
        {disabled
          ? <button className="stop-btn" onClick={onStop} title="Stop generation">■</button>
          : <button className="send-btn" onClick={submit} title="Send (Enter)">↑</button>
        }
      </div>
      <p className="input-hint">{disabled ? 'Click ■ to stop · response streaming…' : 'Enter to send · Shift+Enter for newline'}</p>
    </div>
  )
}
