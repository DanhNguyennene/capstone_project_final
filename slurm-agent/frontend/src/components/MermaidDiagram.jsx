// components/MermaidDiagram.jsx
import { useEffect, useId, useRef } from 'react'
import mermaid from 'mermaid'

mermaid.initialize({ startOnLoad: false, theme: 'default', securityLevel: 'loose' })

export default function MermaidDiagram({ code }) {
  const ref  = useRef(null)
  const raw  = useId()
  const uid  = 'mmd' + raw.replace(/[^a-z0-9]/gi, '')

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
