// hooks/useStream.js
// Handles sending a message, consuming the SSE stream, and accumulating state.

import { useRef } from 'react'
import { streamChat } from '../api'
import { loadSessions, mkMsg } from '../lib/storage'

export function useStream({
  agentUrl,
  mcpUrl,
  llmProvider,
  llmMainProvider,
  llmSpecialistProvider,
  llmJudgeProvider,
  llmMainModel,
  llmSpecialistModel,
  llmJudgeModel,
  openaiParallel,
  activeIdRef,
  setSessions,
  setStreaming,
  setStatus,
  patchMsg,
  createSession,
  onTodoUpdate,
}) {
  const abortRef = useRef(null)

  async function sendMessage(text, hitlDecision = null) {
    if (!text.trim()) return

    let sid = activeIdRef.current
    if (!sid || !loadSessions()[sid]) sid = createSession()

    // Auto-title on first message
    const isFirst = (loadSessions()[sid]?.messages?.length ?? 0) === 0
    const title   = isFirst ? text.slice(0, 44) + (text.length > 44 ? '…' : '') : undefined

    // HITL actions don't show a user message bubble — only an assistant response
    const asstMsg = { ...mkMsg('assistant'), streaming: true }

    setSessions(prev => {
      const s = prev[sid] || { id: sid, title: 'New Chat', messages: [], created: Date.now() }
      const newMsgs = hitlDecision
        ? [...s.messages, asstMsg]
        : [...s.messages, mkMsg('user', text), asstMsg]
      return {
        ...prev,
        [sid]: {
          ...s,
          ...(title ? { title } : {}),
          messages: newMsgs,
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
      let charts   = []
      let inThink  = false

      for await (const delta of streamChat(
        agentUrl,
        sid,
        text,
        controller.signal,
        mcpUrl,
        llmProvider,
        llmMainModel,
        llmSpecialistModel,
        llmJudgeModel,
        hitlDecision,
        llmMainProvider,
        llmSpecialistProvider,
        llmJudgeProvider,
        openaiParallel,
      )) {
        // Reasoning tokens
        if (delta.reasoning_content || delta.reasoning)
          thinking += delta.reasoning_content ?? delta.reasoning

        // Tool step trace
        if (delta.status_update) {
          const s = delta.status_update
          if (steps.length === 0 || steps[steps.length - 1]?.text !== s)
            steps = [...steps, { type: 'step', text: s }]
        }

        // Raw tool output (terminal display)
        if (delta.tool_output) {
          steps = [...steps, { type: 'output', text: delta.tool_output }]
        }

        // Pending actions for confirm/cancel buttons
        if (delta.pending_actions)
          patchMsg(sid, asstMsg.id, { pendingActions: delta.pending_actions })

        // Chart artifacts (mermaid code, sent separately from content)
        if (delta.chart_artifact) {
          charts = [...charts, delta.chart_artifact]
        }

        // Todo list updates (session-level, not per-message)
        if (delta.todo_update) {
          onTodoUpdate?.(delta.todo_update)
        }

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
                m.id === asstMsg.id ? { ...m, thinking, content, steps, charts } : m
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

  function handleAction(decision) {
    // Clear pending-action buttons from all messages so they don't persist
    const sid = activeIdRef.current
    if (sid) {
      setSessions(prev => {
        const s = prev[sid]
        if (!s) return prev
        return {
          ...prev,
          [sid]: {
            ...s,
            messages: s.messages.map(m =>
              m.pendingActions?.length ? { ...m, pendingActions: [] } : m
            ),
          },
        }
      })
    }
    // Send with structured HITL decision so backend doesn't need to parse text
    const label = decision === 'approve' ? 'Confirmed' : 'Cancelled'
    sendMessage(label, decision)
  }

  return { sendMessage, handleAction, abortRef }
}
