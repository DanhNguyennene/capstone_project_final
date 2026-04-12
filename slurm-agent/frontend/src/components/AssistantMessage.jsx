// components/AssistantMessage.jsx
import { memo } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import 'highlight.js/styles/github.min.css'

import MermaidDiagram from './MermaidDiagram'
import ThinkingBlock  from './ThinkingBlock'
import StepsList      from './StepsList'
import ActionButtons  from './ActionButtons'

// Pre-process content: [IMG]url[/IMG] → standard markdown image
function processContent(text) {
  return text.replace(/\[IMG\]([\s\S]*?)\[\/IMG\]/g, (_, src) => `![Chart](${src.trim()})`)
}

function domain(url) {
  try { return new URL(url).hostname } catch { return url }
}

const MarkdownComponents = {
  code({ className, children, ...props }) {
    if (className?.includes('language-mermaid'))
      return <MermaidDiagram code={String(children).trim()} />
    return <code className={className} {...props}>{children}</code>
  },
}

const AssistantMessage = memo(function AssistantMessage({ msg, onAction }) {
  const hasThinking  = !!msg.thinking
  const hasContent   = !!msg.content
  const hasSteps     = !!msg.steps?.length
  const hasCharts    = !!msg.charts?.length

  return (
    <div className="row row-assistant">
      <div className="bubble bubble-assistant">

        {hasThinking && (
          <ThinkingBlock text={msg.thinking} isStreaming={msg.streaming && !hasContent} />
        )}

        <div className="md-content">
          {hasSteps && (
            <StepsList steps={msg.steps} isStreaming={msg.streaming && !hasContent} />
          )}

          {hasContent && (
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[[rehypeHighlight, { ignoreMissing: true }]]}
              components={MarkdownComponents}
            >
              {processContent(msg.content)}
            </ReactMarkdown>
          )}

          {hasCharts && (
            <div className="chart-artifacts">
              {msg.charts.map((code, i) => (
                <MermaidDiagram key={i} code={code.trim()} />
              ))}
            </div>
          )}

          {msg.streaming && !hasThinking && !hasContent && !hasSteps && (
            <span className="loading-dots"><span /><span /><span /></span>
          )}

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

export default AssistantMessage
