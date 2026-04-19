# Job Dependencies and Workflows

**When to use:** User asks about job dependencies, pipelines, workflows, or chaining jobs.

## Key Concepts
- `#SBATCH --dependency=afterok:<job_id>` — run only if <job_id> succeeds.
- Dependency types:
  - `after:<id>` — start after job begins (not finishes).
  - `afterok:<id>` — start only if job completed with exit 0.
  - `afternotok:<id>` — start only if job failed (for cleanup/alerts).
  - `afterany:<id>` — start after job finishes regardless of status.
  - `aftercorr:<id>` — for array jobs: task N starts after task N of dependency.
  - `singleton` — only one job of this name+user runs at a time.
- Chain multiple: `--dependency=afterok:100:200` (after both 100 AND 200 succeed).
- OR logic: `--dependency=afterok:100?afterok:200` (after 100 OR 200 succeed).

## Steps
1. If job is pending with `Dependency` reason, call `scontrol_show(entity="job", id=<id>)` to see the Dependency field.
2. Trace the parent job: is it still running, completed, or failed?
3. If parent failed and dependency is `afterok`, this job will NEVER run → user must cancel it.
4. For `DependencyNeverSatisfied`, the parent was cancelled/failed. Cancel and resubmit.

## Pipeline Example
```bash
# Step 1: preprocess
JOB1=$(sbatch --parsable preprocess.sh)

# Step 2: train (only after preprocess succeeds)
JOB2=$(sbatch --parsable --dependency=afterok:$JOB1 train.sh)

# Step 3: evaluate (after train succeeds)
JOB3=$(sbatch --parsable --dependency=afterok:$JOB2 evaluate.sh)

# Cleanup: runs if anything fails
sbatch --dependency=afternotok:$JOB1:$JOB2:$JOB3 cleanup.sh
```

## Singleton Pattern (prevent duplicates)
```bash
#SBATCH --job-name=daily_backup
#SBATCH --dependency=singleton
```

## Output Format
Show dependency chain with job IDs and their states.
