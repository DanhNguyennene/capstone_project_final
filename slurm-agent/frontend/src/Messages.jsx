import { useState, useEffect, useRef, useId, memo } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import mermaid from 'mermaid'
import 'highlight.js/styles/github.min.css'

mermaid.initialize({ startOnLoad: false, theme: 'default', securityLevel: 'loose' })

// ── Mermaid diagram renderer ───────────────────────────────────────
function MermaidDiagram({ code }) {
  const ref  = useRef(null)
  const rawId = useId()
  const uid  = 'mmd' + rawId.replace(/[^a-z0-9]/gi, '')

  useEffect(() => {
    if (!ref.current) return
    let cancelled = false
    ref.current.innerHTML = '<span class="mermaid-loading">Rendering diagram…</span>'
    mermaid.render(uid, code)
      .then(({ svg }) => { if (!cancelled && ref.current) ref.current.innerHTML = svg })
      .catch(() => { if (!cancelled && ref.current) ref.current.textContent = code })
    return () => { cancelled = true }
  }, [code, uid])

  return <div className="mermaid-wrap" ref={ref} />
}

// ── Custom markdown components ─────────────────────────────────────
const MarkdownComponents = {
  // Intercept mermaid fenced code blocks before highlight.js touches them
  code({ className, children, ...props }) {
    if (className?.includes('language-mermaid')) {
      return <MermaidDiagram code={String(children).trim()} />
    }
    return <code className={className} {...props}>{children}</code>
  },
}

// Pre-process agent content: [IMG]url[/IMG] → standard md image
function processContent(text) {
  return text.replace(/\[IMG\]([\s\S]*?)\[\/IMG\]/g, (_, src) => `![Chart](${src.trim()})`)
}

function domain(url) {
  try { return new URL(url).hostname } catch { return url }
}

// ── Collapsible thinking block ─────────────────────────────────────
function ThinkingBlock({ text, isStreaming }) {
  const [open, setOpen] = useState(true) // default open while streaming

  // Auto-collapse when streaming finishes
  const prevStreaming = useRef(isStreaming)
  useEffect(() => {
    if (prevStreaming.current && !isStreaming) setOpen(false)
    prevStreaming.current = isStreaming
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

// ── Confirm / Cancel action buttons ──────────────────────────────
function ActionButtons({ actions, onAction }) {
  if (!actions?.length) return null
  return (
    <div className="action-row">
      <span className="action-label">⚠️ Awaiting your confirmation:</span>
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

// ── Status line (tool / agent activity, not model reasoning) ───────
function StatusLine({ text }) {
  if (!text) return null
  return (
    <div className="status-line">
      <span className="status-spinner" />
      {text}
    </div>
  )
}

// ── User message ───────────────────────────────────────────────────
const UserMessage = memo(function UserMessage({ content }) {
  return (
    <div className="row row-user">
      <div className="bubble bubble-user">{content}</div>
    </div>
  )
})

// ── Assistant message ──────────────────────────────────────────────
const AssistantMessage = memo(function AssistantMessage({ msg, onAction }) {
  const hasThinking = !!msg.thinking
  const hasContent  = !!msg.content

  return (
    <div className="row row-assistant">
      <div className="bubble bubble-assistant">

        {/* Real model reasoning — only when present */}
        {hasThinking && (
          <ThinkingBlock text={msg.thinking} isStreaming={msg.streaming && !hasContent} />
        )}

        <div className="md-content">
          {hasContent && (
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[[rehypeHighlight, { ignoreMissing: true }]]}
              components={MarkdownComponents}
            >
              {processContent(msg.content)}
            </ReactMarkdown>
          )}

          {/* Status line — tool / agent activity while streaming */}
          {msg.streaming && msg.statusText && !hasContent && (
            <StatusLine text={msg.statusText} />
          )}

          {/* Fallback dots when absolutely nothing else is showing */}
          {msg.streaming && !hasThinking && !hasContent && !msg.statusText && (
            <span className="loading-dots"><span /><span /><span /></span>
          )}

          {/* Streaming cursor when content is flowing */}
          {msg.streaming && hasContent && <span className="cursor" />}
        </div>

        {msg.webResults?.length > 0 && (
          <div className="web-results">
            🔍{' '}
            {msg.webResults.map((u, i) => (
              <a key={i} href={u} target="_blank" rel="noopener noreferrer">
                {domain(u)}
              </a>
            ))}
          </div>
        )}

        {!msg.streaming && msg.pendingActions?.length > 0 && (
          <ActionButtons actions={msg.pendingActions} onAction={onAction} />
        )}
      </div>
    </div>
  )
})

// ── Suggestion starters ────────────────────────────────────────────
const SUGGESTIONS = [
  'Show all running jobs',
  'Why is my job pending?',
  'Show cluster resource usage',
  'Generate a system health chart',
  'List failed jobs today',
  'Show GPU resource availability',
]

// ── Messages container ─────────────────────────────────────────────
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
            <button key={s} className="suggestion" onClick={() => onSuggestion(s)}>
              {s}
            </button>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="messages">
      {messages.map(m =>
        m.role === 'user'
          ? <UserMessage    key={m.id} content={m.content} />
          : <AssistantMessage key={m.id} msg={m} onAction={onAction} />
      )}
      <div ref={bottomRef} />
    </div>
  )
}
