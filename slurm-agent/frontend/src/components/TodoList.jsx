// components/TodoList.jsx
// Visual task plan showing the agent's progress through a multi-step workflow.
// Items show: ○ not-started, ⏳ in-progress (spinner), ✓ completed
// Collapses automatically when all done; can be dismissed with × button.

import { useState, useEffect } from 'react'

export default function TodoList({ items, isStreaming }) {
  const [dismissed, setDismissed] = useState(false)
  const [collapsed, setCollapsed] = useState(false)

  // Reset dismiss when a NEW plan arrives (different item count or ids)
  useEffect(() => {
    setDismissed(false)
    setCollapsed(false)
  }, [items?.length, items?.[0]?.id])

  if (!items?.length || dismissed) return null

  const doneCount = items.filter(i => i.status === 'completed').length
  const allDone = doneCount === items.length
  const inProg = items.find(i => i.status === 'in-progress')

  return (
    <div className={`todo-list ${allDone ? 'todo-all-done' : ''}`}>
      <div className="todo-header-row" onClick={() => setCollapsed(c => !c)}>
        <span className="todo-header">
          Plan
          <span className="todo-count">{doneCount}/{items.length}</span>
        </span>
        <span className="todo-header-actions">
          <button
            className="todo-collapse-btn"
            title={collapsed ? 'Expand' : 'Collapse'}
            onClick={(e) => { e.stopPropagation(); setCollapsed(c => !c) }}
          >
            {collapsed ? '▸' : '▾'}
          </button>
          <button
            className="todo-dismiss-btn"
            title="Dismiss"
            onClick={(e) => { e.stopPropagation(); setDismissed(true) }}
          >
            ×
          </button>
        </span>
      </div>
      {!collapsed && items.map((item) => {
        const isActive = item.status === 'in-progress'
        const isDone = item.status === 'completed'
        return (
          <div
            key={item.id}
            className={`todo-item ${isActive ? 'todo-active' : ''} ${isDone ? 'todo-done' : ''}`}
          >
            {isDone ? (
              <span className="todo-check">✓</span>
            ) : isActive ? (
              <span className="todo-spinner" />
            ) : (
              <span className="todo-circle">○</span>
            )}
            <span className="todo-text">{item.title}</span>
          </div>
        )
      })}
    </div>
  )
}
