// hooks/useStream.js
// Handles sending a message, consuming the SSE stream, and accumulating state.

import { useRef } from 'react'
import { streamChat } from '../api'
import { loadSessions, mkMsg } from '../lib/storage'

export function useStream({
  agentUrl,
  activeIdRef,
  setSessions,
  setStreaming,
  setStatus,
  patchMsg,
  createSession,
}) {
  const abortRef = useRef(null)

  async function sendMessage(text) {
    if (!text.trim()) return

    let sid = activeIdRef.current
    if (!sid || !loadSessions()[sid]) sid = createSession()

    // Auto-title on first message
    const isFirst = (loadSessions()[sid]?.messages?.length ?? 0) === 0
    const title   = isFirst ? text.slice(0, 44) + (text.length > 44 ? '…' : '') : undefined

    const userMsg = mkMsg('user', text)
    const asstMsg = { ...mkMsg('assistant'), streaming: true }

    setSessions(prev => {
      const s = prev[sid] || { id: sid, title: 'New Chat', messages: [], created: Date.now() }
      return {
        ...prev,
        [sid]: {
          ...s,
          ...(title ? { title } : {}),
          messages: [...s.messages, userMsg, asstMsg],
        },
      }
    })

    setStreaming(true)
    setStatus({ state: 'thinking', text: 'Thinking…' })

    const controller = new AbortController()
    abortRef.current = controller

    try {
      let thinking = ''
      let content  = ''
      let steps    = []
      let inThink  = false

      for await (const delta of streamChat(agentUrl, sid, text, controller.signal)) {
        // Reasoning tokens
        if (delta.reasoning_content || delta.reasoning)
          thinking += delta.reasoning_content ?? delta.reasoning

        // Tool step trace
        if (delta.status_update) {
          const s = delta.status_update
          if (steps.length === 0 || steps[steps.length - 1] !== s)
            steps = [...steps, s]
        }

        // Pending actions for confirm/cancel buttons
        if (delta.pending_actions)
          patchMsg(sid, asstMsg.id, { pendingActions: delta.pending_actions })

        // Content (with inline <think> routing)
        if (delta.content) {
          let chunk = delta.content
          let processed = ''
          while (chunk.length > 0) {
            if (inThink) {
              const end = chunk.indexOf('</think>')
              if (end === -1) { thinking += chunk; chunk = '' }
              else { thinking += chunk.slice(0, end); chunk = chunk.slice(end + 8); inThink = false }
            } else {
              const start = chunk.indexOf('<think>')
              if (start === -1) { processed += chunk; chunk = '' }
              else { processed += chunk.slice(0, start); chunk = chunk.slice(start + 7); inThink = true }
            }
          }
          content += processed
        }

        // Batch update message (avoids N setSessions calls per token)
        setSessions(prev => {
          const s = prev[sid]
          if (!s) return prev
          return {
            ...prev,
            [sid]: {
              ...s,
              messages: s.messages.map(m =>
                m.id === asstMsg.id ? { ...m, thinking, content, steps } : m
              ),
            },
          }
        })
      }
    } catch (err) {
      if (err.name === 'AbortError') {
        patchMsg(sid, asstMsg.id, { streaming: false })
        setStatus({ state: 'online', text: 'Ready' })
      } else {
        patchMsg(sid, asstMsg.id, { content: `⚠ ${err.message}`, streaming: false })
        setStatus({ state: 'offline', text: 'Error' })
      }
      setStreaming(false)
      return
    }

    patchMsg(sid, asstMsg.id, { streaming: false })
    setStreaming(false)
    setStatus({ state: 'online', text: 'Ready' })
  }

  function handleAction(actionText) {
    sendMessage(actionText)
  }

  return { sendMessage, handleAction, abortRef }
}
