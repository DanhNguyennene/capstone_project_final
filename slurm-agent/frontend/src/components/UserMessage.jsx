// components/UserMessage.jsx
import { memo } from 'react'

const FILE_RE = /\[Attached file: ([^\]]+)\]/g

const UserMessage = memo(function UserMessage({ content }) {
  // Extract attached files and remaining text
  const files = []
  let match
  while ((match = FILE_RE.exec(content)) !== null) files.push(match[1])
  const text = content.replace(FILE_RE, '').trim()

  return (
    <div className="row row-user">
      <div className="bubble bubble-user">
        {files.length > 0 && (
          <div className="msg-files">
            {files.map((f, i) => (
              <span key={i} className="msg-file-chip">📄 {f.split('/').pop()}</span>
            ))}
          </div>
        )}
        {text}
      </div>
    </div>
  )
})

export default UserMessage
