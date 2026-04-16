# Manual End-to-End Test Cases
> 20 simple, runnable scenarios. Each is a natural user request → agent acts → verify outcome.
> All scripts fit **danhHomeBase**: 12 CPUs, 63000 MB (~60G), 1× RTX 5070 Ti, partitions: debug*, gpu, cpu.
> The agent chooses its own tools. `shell_exec` should only appear as a last resort.

---

## Setup

```bash
# 1. Copy scripts
mkdir -p /tmp/slurm_uploads
cp evaluation/scripts/*.sh /tmp/slurm_uploads/

# 2. Start MCP server (pick one)
cd mcp-server && python slurm_mcp_sse.py --real --port 3002        # real Slurm
cd mcp-server && python slurm_mcp_sse.py --mock debug_needed       # mock

# 3. Start agent
cd agent && python main.py

# 4. Pre-fail jobs for diagnosis tests (14, 18)
sbatch /tmp/slurm_uploads/bad_script.sh      # note ID → TEST 14
sbatch /tmp/slurm_uploads/memory_hog.sh      # wait for OOM → TEST 18
```

---

## TEST 1 — Submit a Simple Job

```
[Attached file: /tmp/slurm_uploads/hello_world.sh]
Submit this job.
```

**Pass criteria:**
- [ ] Job submitted
- [ ] Job ID returned
- [ ] No unnecessary questions asked

---

## TEST 2 — Submit + Check Status

```
[Attached file: /tmp/slurm_uploads/hello_world.sh]
Submit this and tell me its status.
```

**Pass criteria:**
- [ ] Job submitted
- [ ] Agent checked status after submit
- [ ] Response includes job state (PENDING/RUNNING/COMPLETED)

---

## TEST 3 — GPU Job

```
[Attached file: /tmp/slurm_uploads/gpu_benchmark.sh]
Run this on the gpu partition with 1 GPU.
```

**Pass criteria:**
- [ ] Job submitted with `--gres=gpu:1` and `--partition=gpu`
- [ ] Job ID returned

---

## TEST 4 — Check Queue

```
What's running right now? Show me the queue.
```

**Pass criteria:**
- [ ] Agent queried the queue
- [ ] Response shows running/pending jobs
- [ ] No Operator handoff (read-only)
- [ ] Did NOT use `shell_exec` for this

---

## TEST 5 — Check Cluster Resources

```
Show me the cluster resources — CPUs, memory, GPUs available.
```

**Pass criteria:**
- [ ] Agent checked resources
- [ ] Response shows CPU/memory/GPU info
- [ ] No Operator handoff (read-only)

---

## TEST 6 — Two-Job Dependency

```
[Attached file: /tmp/slurm_uploads/multi_step.sh]
[Attached file: /tmp/slurm_uploads/backup_cleanup.sh]

Submit multi_step.sh first, then backup_cleanup.sh after it finishes successfully.
```

**Pass criteria:**
- [ ] 2 jobs submitted
- [ ] Second job has `afterok` dependency on first
- [ ] Both job IDs shown

---

## TEST 7 — Cancel a Job

**Multi-turn.**

**Turn 1:**
```
[Attached file: /tmp/slurm_uploads/long_simulation.sh]
Submit this simulation.
```

**Turn 2:**
```
Cancel job <ID>.
```

**Pass criteria:**
- [ ] Job submitted (Turn 1)
- [ ] Job cancelled (Turn 2)
- [ ] Confirmation shown

---

## TEST 8 — Diagnose a Failed Job

**Pre-condition:** `sbatch /tmp/slurm_uploads/bad_script.sh` — note the job ID.

```
Job <ID> failed. Why?
```

**Pass criteria:**
- [ ] Agent investigated the failure
- [ ] Exit code mentioned
- [ ] Plausible explanation given
- [ ] Did NOT just run `shell_exec` to cat logs as first action

---

## TEST 9 — Hold + Release

**Multi-turn.**

**Turn 1:**
```
[Attached file: /tmp/slurm_uploads/file_processor.sh]
Submit this but hold it immediately.
```

**Turn 2:**
```
Release job <ID>.
```

**Pass criteria:**
- [ ] Job submitted and held (Turn 1)
- [ ] Job released (Turn 2)
- [ ] No "are you sure?" asked

---

## TEST 10 — Array Job

```
[Attached file: /tmp/slurm_uploads/hyperparam_sweep.sh]
Submit as array 0-11, max 4 concurrent, gpu partition, 1 GPU, 4G memory.
```

**Pass criteria:**
- [ ] Job submitted
- [ ] Array spec includes `0-11%4`
- [ ] GPU + partition flags present

---

## TEST 11 — 4-Stage ML Pipeline

```
[Attached file: /tmp/slurm_uploads/data_download.sh]
[Attached file: /tmp/slurm_uploads/preprocess.sh]
[Attached file: /tmp/slurm_uploads/train_gpu.sh]
[Attached file: /tmp/slurm_uploads/evaluate.sh]

Submit a 4-stage ML pipeline:
1. data_download first
2. preprocess after download succeeds
3. train_gpu after preprocess, gpu partition, 1 GPU, 16G mem, 1 hour
4. evaluate after train regardless of success/failure

Show the dependency chain.
```

**Pass criteria:**
- [ ] 4 jobs submitted
- [ ] All 4 job IDs in response
- [ ] `afterok` dependency on jobs 2 and 3
- [ ] `afterany` dependency on job 4
- [ ] Summary/chain shown

---

## TEST 12 — OOM Requeue

**Pre-condition:** `sbatch /tmp/slurm_uploads/memory_hog.sh` — wait for OOM, note ID.

```
Job <ID> got OOM killed. Requeue with double the memory.
```

**Pass criteria:**
- [ ] Agent identified OOM
- [ ] Job requeued/resubmitted with 2× memory
- [ ] Confirmation shown

---

## TEST 13 — Cluster Health Overview

```
Give me a full cluster health check: nodes, queue, resources.
```

**Pass criteria:**
- [ ] Node states shown
- [ ] Queue summary shown
- [ ] Resource availability shown
- [ ] No Operator handoff

---

## TEST 14 — Submit + Monitor Until Done

```
[Attached file: /tmp/slurm_uploads/health_check.sh]
Submit this and check on it until it finishes.
```

**Pass criteria:**
- [ ] Job submitted
- [ ] Agent checked status at least once after submit
- [ ] Final state reported (COMPLETED or similar)

---

## TEST 15 — Node Info

```
Show me details about node danhHomeBase — CPUs, memory, GPU, current state.
```

**Pass criteria:**
- [ ] Node details shown (CPUs, mem, GPU, state)
- [ ] No Operator handoff
- [ ] Correct info matches system (12 CPUs, ~63G, 1 GPU)

---

## TEST 16 — Submit with Custom Flags

```
[Attached file: /tmp/slurm_uploads/file_processor.sh]
Submit this with 2 CPUs, 2G memory, 10 minute walltime, on the cpu partition.
```

**Pass criteria:**
- [ ] Job submitted
- [ ] Flags match: `--cpus-per-task=2 --mem=2G --time=00:10:00 --partition=cpu`

---

## TEST 17 — Diagnose + Resubmit

**Multi-turn.**

**Turn 1:**
Pre-condition: `sbatch /tmp/slurm_uploads/bad_script.sh` — note the job ID.
```
Job <ID> failed. What happened?
```

**Turn 2:**
```
Fix whatever was wrong and resubmit it.
```

**Pass criteria:**
- [ ] Failure diagnosed (Turn 1)
- [ ] Agent attempted to fix/resubmit (Turn 2)
- [ ] New job ID returned (Turn 2)

---

## TEST 18 — Batch File Processing

```
[Attached file: /tmp/slurm_uploads/file_processor.sh]
Run this file processor on the cpu partition with 4G memory.
```

**Pass criteria:**
- [ ] Job submitted
- [ ] Correct partition and memory flags
- [ ] Job ID returned

---

## TEST 19 — Job History

```
Show me my recent job history — what ran, what failed, what's pending.
```

**Pass criteria:**
- [ ] Agent queried accounting/queue data
- [ ] Response shows job states (completed/failed/pending)
- [ ] No Operator handoff

---

## TEST 20 — Drain and Resume Node

**Multi-turn.**

**Turn 1:**
```
Drain node danhHomeBase with reason "scheduled maintenance".
```

**Turn 2:**
```
OK maintenance done. Resume the node.
```

**Pass criteria:**
- [ ] Node drained (Turn 1)
- [ ] Reason included in drain command
- [ ] Node resumed (Turn 2)
- [ ] HITL approval requested for both operations

---

## Notes

- **Multi-turn tests:** 7, 9, 17, 20 need the same chat session.
- **Pre-fail tests:** 8, 12 require a job to fail first (see Setup).
- **HITL:** Any write operation (submit, cancel, hold, drain, requeue) should trigger approval.
- **Tool choice:** The agent picks its own tools. Pass criteria check outcomes, not specific tool names.
- **Mock mode:** Use `--mock debug_needed` for tests that reference failed/OOM jobs on a mock cluster.
