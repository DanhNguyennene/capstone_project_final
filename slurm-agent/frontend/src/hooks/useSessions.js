// hooks/useSessions.js
// Session CRUD, localStorage sync, and message patching.

import { useEffect, useState } from 'react'
import { ACTIVE_KEY, SESSIONS_KEY, loadSessions, mkId } from '../lib/storage'
import { clearSessionOnServer } from '../api'

export function useSessions() {
  const [sessions, setSessions] = useState(() => loadSessions())
  const [activeId, setActiveId] = useState(() => localStorage.getItem(ACTIVE_KEY))

  // Persist to localStorage
  useEffect(() => { localStorage.setItem(SESSIONS_KEY, JSON.stringify(sessions)) }, [sessions])
  useEffect(() => { if (activeId) localStorage.setItem(ACTIVE_KEY, activeId) }, [activeId])

  // ── CRUD ─────────────────────────────────────────────────────────────────
  function createSession() {
    const id = mkId()
    setSessions(prev => ({
      ...prev,
      [id]: { id, title: 'New Chat', messages: [], created: Date.now() },
    }))
    setActiveId(id)
    return id
  }

  function selectSession(id) { setActiveId(id) }

  function deleteSession(id) {
    setSessions(prev => {
      const next = { ...prev }
      delete next[id]
      return next
    })
    if (activeId === id) {
      const remaining = Object.keys(sessions).filter(k => k !== id)
      remaining.length > 0 ? setActiveId(remaining[0]) : createSession()
    }
  }

  async function clearSession(agentUrl, id) {
    if (!id) return
    if (!confirm('Clear this chat?')) return
    setSessions(prev => ({
      ...prev,
      [id]: { ...prev[id], messages: [], title: 'New Chat' },
    }))
    clearSessionOnServer(agentUrl, id).catch(() => {})
  }

  // ── Message utilities ─────────────────────────────────────────────────────
  function patchMsg(sid, msgId, patch) {
    setSessions(prev => {
      const s = prev[sid]
      if (!s) return prev
      return {
        ...prev,
        [sid]: {
          ...s,
          messages: s.messages.map(m => m.id === msgId ? { ...m, ...patch } : m),
        },
      }
    })
  }

  // ── Derived ───────────────────────────────────────────────────────────────
  const sessionList    = Object.values(sessions).sort((a, b) => b.created - a.created)
  const currentSession = sessions[activeId]

  return {
    sessions, setSessions,
    activeId, setActiveId,
    sessionList, currentSession,
    createSession, selectSession, deleteSession, clearSession,
    patchMsg,
  }
}
