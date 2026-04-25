import { useRef, useState, useCallback } from 'react'
import { uploadFile } from './api'

export default function InputBar({ onSend, disabled, onStop, agentUrl }) {
  const ref = useRef(null)
  const fileRef = useRef(null)
  const [files, setFiles] = useState([])       // [{name, path, uploading}]
  const [dragging, setDragging] = useState(false)

  function submit() {
    const text = ref.current?.value.trim()
    if ((!text && files.length === 0) || disabled) return
    // Build message: prepend file paths so the agent knows about them
    const filePaths = files.filter(f => f.path).map(f => f.path)
    let msg = text || ''
    if (filePaths.length > 0) {
      const fileInfo = filePaths.map(p => `[Attached file: ${p}]`).join('\n')
      msg = fileInfo + (msg ? '\n' + msg : '\nPlease review this job script.')
    }
    onSend(msg)
    ref.current.value = ''
    ref.current.style.height = 'auto'
    setFiles([])
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

  const processFiles = useCallback(async (fileList) => {
    for (const file of fileList) {
      const entry = { name: file.name, path: null, uploading: true, error: null }
      setFiles(prev => [...prev, entry])
      try {
        const result = await uploadFile(agentUrl, file)
        setFiles(prev => prev.map(f =>
          f.name === file.name && f.uploading ? { ...f, path: result.path, uploading: false } : f
        ))
      } catch (err) {
        setFiles(prev => prev.map(f =>
          f.name === file.name && f.uploading ? { ...f, uploading: false, error: err.message } : f
        ))
      }
    }
  }, [agentUrl])

  function handleDrop(e) {
    e.preventDefault()
    setDragging(false)
    if (e.dataTransfer.files.length > 0) processFiles(e.dataTransfer.files)
  }

  function handleDragOver(e) { e.preventDefault(); setDragging(true) }
  function handleDragLeave() { setDragging(false) }

  function handleFileInput(e) {
    if (e.target.files.length > 0) processFiles(e.target.files)
    e.target.value = ''
  }

  function removeFile(idx) {
    setFiles(prev => prev.filter((_, i) => i !== idx))
  }

  return (
    <div className="input-area"
      onDrop={handleDrop} onDragOver={handleDragOver} onDragLeave={handleDragLeave}>
      {dragging && <div className="drop-overlay">Drop files here</div>}
      {files.length > 0 && (
        <div className="file-chips">
          {files.map((f, i) => (
            <span key={i} className={`file-chip${f.error ? ' file-chip-error' : ''}`}>
              📄 {f.name}
              {f.uploading && <span className="file-uploading">…</span>}
              {f.error && <span className="file-error" title={f.error}>⚠</span>}
              <button className="file-remove" onClick={() => removeFile(i)}>×</button>
            </span>
          ))}
        </div>
      )}
      <div className={`input-wrap${disabled ? ' input-wrap-disabled' : ''}`}>
        <button className="attach-btn" onClick={() => fileRef.current?.click()}
          disabled={disabled} title="Attach file">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48"/>
          </svg>
        </button>
        <input ref={fileRef} type="file" hidden multiple accept=".sh,.bash,.py,.txt,.sbatch,.job,.slurm,image/*,.png,.jpg,.jpeg,.webp,.gif,.bmp,.tif,.tiff"
          onChange={handleFileInput} />
        <textarea
          ref={ref}
          className="input-box"
          rows={1}
          placeholder={disabled ? 'Waiting for response…' : 'Ask about your cluster… (drop files here)'}
          onKeyDown={handleKey}
          onInput={autoResize}
          disabled={disabled}
        />
        {disabled
          ? <button className="stop-btn" onClick={onStop} title="Stop generation">■</button>
          : <button className="send-btn" onClick={submit} title="Send (Enter)">↑</button>
        }
      </div>
      <p className="input-hint">{disabled ? 'Click ■ to stop · response streaming…' : 'Enter to send · Shift+Enter for newline · Drop or 📎 to attach files/images · /todo and /skill commands supported'}</p>
    </div>
  )
}
