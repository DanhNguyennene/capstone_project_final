// components/TodoList.jsx
// Visual task plan showing the agent's progress through a multi-step workflow.
// Items show: ○ not-started, ⏳ in-progress (spinner), ✓ completed

export default function TodoList({ items, isStreaming }) {
  if (!items?.length) return null
  return (
    <div className="todo-list">
      <div className="todo-header">Plan</div>
      {items.map((item) => {
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
