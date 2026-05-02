# Node Drain and Maintenance

**When to use:** You are asked to drain a node (take it offline), bring a node back online (undrain/resume), set a node DOWN, or reboot a node for maintenance.

## Available Tools
- `scontrol_node(node=<node>, state=<state>, reason=<reason>)` — set administrative node state
- `scontrol_node_weight(node=<node>, weight=<number>)` — update scheduling weight
- `scontrol_show(entity="node", id=<node>)` — verify node state before/after

## Key State Transitions
| Goal | Command params |
|---|---|
| Drain (no new jobs, existing finish) | `State=DRAIN Reason="<reason>"` |
| Undrain (re-enable after drain) | `State=RESUME` |
| Mark DOWN (kill jobs, unavailable) | `State=DOWN Reason="<reason>"` |
| Bring back from DOWN | `State=RESUME` |
| Set IDLE (force ready) | `State=IDLE` |

## Workflows

### Drain a single node
```
scontrol_node(node="<nodename>", state="DRAIN", reason="maintenance scheduled")
```

### Drain multiple nodes (range expression)
```
scontrol_node(node="node[01-04]", state="DRAIN", reason="hw fault")
```

### Resume (undrain) a node
```
scontrol_node(node="<nodename>", state="RESUME")
```

### Mark node DOWN immediately
```
scontrol_node(node="<nodename>", state="DOWN", reason="network failure")
```

### Update node weight (affects scheduling preference)
```
scontrol_node_weight(node="<nodename>", weight=<number>)
```
Lower weight = preferred for allocation.

### Reboot a node when it becomes idle
```
scontrol_node(node="<nodename>", state="DRAIN", reason="reboot pending")
```
Then after drain completes, reboot via OS and resume with `state="RESUME"`.

## Verification
```
scontrol_show(entity="node", id="<nodename>")
```
Check `State` field: expected values include `IDLE`, `DRAIN`, `DRAINING`, `DRAINED`, `DOWN`, `ALLOCATED`.

## After Actions
Report: Node | Previous State | New State | Reason — in a markdown table.
Always call `transfer_to_observer` after so observer can verify the queue impact.
