# Walltime and Checkpointing

**When to use:** User asks about time limits, job timeouts (exit 143), extending time, or checkpointing.

## Key Concepts
- `--time=DD-HH:MM:SS` — walltime limit. Job is killed with SIGTERM (exit 143) when exceeded.
- Lower walltime = higher scheduling priority (backfill can schedule shorter jobs sooner).
- `--signal=B:USR1@300` — sends SIGUSR1 to batch script 300s before timeout.
- Remaining time: `squeue -j <id> -o "%L"` or `$SLURM_JOB_END_TIME` env var.

## Steps
1. If job failed with exit 143 (SIGTERM), call `sacct(job_id=<id>)` to compare Elapsed vs Timelimit.
2. If Elapsed ≈ Timelimit, walltime was the issue → increase `--time`.
3. Recommend checkpointing for jobs >4h.
4. To extend a running job: `scontrol_update(entity="job", id=<id>, params="TimeLimit=2-00:00:00")`.

## Checkpoint with SIGUSR1
```bash
#SBATCH --time=24:00:00
#SBATCH --signal=B:USR1@600   # 10min warning before kill
#SBATCH --requeue              # auto-requeue on preemption

CHECKPOINT_DIR=checkpoints/$SLURM_JOB_ID

handle_timeout() {
    echo "Saving checkpoint before timeout..."
    python save_checkpoint.py --dir $CHECKPOINT_DIR
    scontrol requeue $SLURM_JOB_ID
    exit 0
}

trap 'handle_timeout' USR1

python train.py --resume-from $CHECKPOINT_DIR &
wait $!
```

## Time Format
- `30` — 30 minutes
- `2:00:00` — 2 hours
- `1-00:00:00` — 1 day
- `7-00:00:00` — 1 week
- `infinite` — no limit (admin only)

## Tips
- Request 10-20% more time than expected to avoid edge cases.
- Use `--time-min` to set minimum acceptable time (for backfill flexibility).
- Short jobs (<1h) get backfilled into gaps — faster scheduling.

## Output Format
Show elapsed vs limit, and checkpoint recommendation.
