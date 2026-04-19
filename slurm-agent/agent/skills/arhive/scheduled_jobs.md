# Scheduled / Recurring Jobs (scrontab)

**When to use:** User asks about recurring jobs, cron-like scheduling, periodic tasks, or scrontab.

## Key Concepts
- `scrontab` is Slurm's built-in cron. Jobs run as sbatch submissions on schedule.
- Must be enabled by admin (`ScronParameters=enable` in slurm.conf).
- Cron syntax: `minute hour day_of_month month day_of_week command`.
- Use `#SCRON` lines for sbatch options before each crontab entry.
- Jobs are not guaranteed exact times — they queue like normal sbatch.
- Next job in series won't submit until previous one completes.

## Steps
1. To view: call `scrontab(action="list")`.
2. To create: call `scrontab(action="edit", content=<crontab_text>)`.
3. To remove: call `scrontab(action="remove")`.
4. To cancel one recurring job: use `scancel <job_id>` — it comments out the entry.
5. To skip next run: `scontrol requeue <job_id>`.

## Example Crontab
```
#SCRON -p gpu
#SCRON -t 2:00:00
#SCRON --gres=gpu:1
0 */6 * * * /home/user/retrain_model.sh

#SCRON -p cpu
#SCRON -t 30:00
@daily /home/user/backup.sh

#SCRON -p cpu
#SCRON -t 5:00
#SCRON --mail-type=FAIL
*/30 * * * * /home/user/health_check.sh
```

## Shortcuts
- `@yearly` / `@annually` — Jan 1 at 00:00
- `@monthly` — 1st of month at 00:00
- `@weekly` — Sunday at 00:00
- `@daily` / `@midnight` — every day at 00:00
- `@hourly` — first minute of every hour

## Output Format
Show the crontab content and schedule summary.
