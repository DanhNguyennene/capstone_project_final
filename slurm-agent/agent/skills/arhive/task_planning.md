# Task Planning with manage_todos

**When to use:** Any multi-step task (health checks, pipeline submissions, bulk operations, investigations with 3+ tool calls). Skip for single-tool lookups.

## How manage_todos Works
- Call `manage_todos(todoList=[...])` with the **complete** list every time.
- Replacing the list is how you create, update, and delete items.
- The frontend renders the list in real-time as a progress panel.
- Schema per item: `{id: int, title: str (3-7 words), status: "not-started"|"in-progress"|"completed"}`

## Critical Rules (mirror Copilot's manage_todo_list)
1. **Plan first** — call `manage_todos` BEFORE the first tool call, not after.
2. **One active at a time** — only one item has `"in-progress"` status.
3. **Mark immediately** — set `"in-progress"` when starting, `"completed"` the moment done.
4. **Full list always** — pass ALL items every call (not just the changed one).
5. **No hardcode** — LLM decides the list content from the request.

## Pattern: Health Check

```
# Start: set plan
manage_todos(todoList=[
  {id:1, title:"Check partition and node states", status:"in-progress"},
  {id:2, title:"Review job queue",                status:"not-started"},
  {id:3, title:"Check scheduler metrics",         status:"not-started"},
  {id:4, title:"Summarize cluster health",        status:"not-started"},
])

# → run sinfo → squeue → sdiag

# After each tool:
manage_todos(todoList=[
  {id:1, title:"Check partition and node states", status:"completed"},
  {id:2, title:"Review job queue",                status:"in-progress"},
  ...
])
```

## Pattern: Pipeline Submit (Operator)

```
manage_todos(todoList=[
  {id:1, title:"Submit data_download.sh",  status:"in-progress"},
  {id:2, title:"Submit preprocess.sh",     status:"not-started"},
  {id:3, title:"Submit train_gpu.sh",      status:"not-started"},
  {id:4, title:"Submit evaluate.sh",       status:"not-started"},
  {id:5, title:"Report all job IDs",       status:"not-started"},
])
```
Then submit one script at a time, updating after each sbatch call.

## Pattern: Investigation with Handoff

```
manage_todos(todoList=[
  {id:1, title:"Identify failing jobs",          status:"in-progress"},
  {id:2, title:"Hand off to Operator to requeue", status:"not-started"},
  {id:3, title:"Verify jobs requeued",            status:"not-started"},
])
```
Mark step 1 completed before calling transfer_to_operator.
