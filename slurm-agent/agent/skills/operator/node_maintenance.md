# Node Drain and Maintenance

**When to use:** You are asked to drain a node (take it offline), bring a node back online (undrain/resume), set a node DOWN, or reboot a node for maintenance.

## Available Tools
- `scontrol_update(entity="node", id=<node>, params=<spec>)` — update node state/properties
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
scontrol_update(entity="node", id="<nodename>", params="State=DRAIN Reason='maintenance scheduled'")
```

### Drain multiple nodes (range expression)
```
scontrol_update(entity="node", id="node[01-04]", params="State=DRAIN Reason='hw fault'")
```

### Resume (undrain) a node
```
scontrol_update(entity="node", id="<nodename>", params="State=RESUME")
```

### Mark node DOWN immediately
```
scontrol_update(entity="node", id="<nodename>", params="State=DOWN Reason='network failure'")
```

### Update node weight (affects scheduling preference)
```
scontrol_update(entity="node", id="<nodename>", params="Weight=<number>")
```
Lower weight = preferred for allocation.

### Reboot a node when it becomes idle
```
scontrol_update(entity="node", id="<nodename>", params="State=DRAIN Reason='reboot pending'")
```
Then after drain completes, reboot via OS and resume: `State=RESUME`.

## Verification
```
scontrol_show(entity="node", id="<nodename>")
```
Check `State` field: expected values include `IDLE`, `DRAIN`, `DRAINING`, `DRAINED`, `DOWN`, `ALLOCATED`.

## After Actions
Report: Node | Previous State | New State | Reason — in a markdown table.
Always call `transfer_to_observer` after so observer can verify the queue impact.
