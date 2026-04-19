# Job Arrays

**When to use:** User asks about job arrays, wants to submit parametric/batch sweeps, or has array job issues.

## Key Concepts
- `#SBATCH --array=0-99` submits 100 tasks sharing one job ID (e.g., 12345_0 through 12345_99).
- `%N` limits concurrency: `--array=0-999%50` runs at most 50 tasks at a time.
- Inside the script: `$SLURM_ARRAY_TASK_ID` gives the current index, `$SLURM_ARRAY_JOB_ID` the parent.
- Cancel one task: `scancel 12345_42`. Cancel all: `scancel 12345`. Cancel a range: `scancel 12345_[10-20]`.
- Hold/release entire array: `scontrol hold/release 12345`.

## Steps
1. If user asks about array syntax, explain `--array=start-end%maxrun` and env vars.
2. If array job is pending with `JobArrayTaskLimit`, the `%N` concurrency cap is reached — wait or increase it.
3. If some tasks failed, call `sacct(job_id="<array_id>")` to see per-task exit codes.
4. If user wants to rerun failed tasks only, use `--array=<failed_indices>` with scontrol_requeue or new sbatch.

## Common Patterns
```bash
#SBATCH --array=0-99%10       # 100 tasks, 10 at a time
#SBATCH --output=logs/%A_%a.out  # %A=job_id, %a=task_id

INPUT_FILE=data/input_${SLURM_ARRAY_TASK_ID}.csv
python train.py --config $INPUT_FILE
```

## Output Format
Show the array syntax, env vars, and any relevant status table.
