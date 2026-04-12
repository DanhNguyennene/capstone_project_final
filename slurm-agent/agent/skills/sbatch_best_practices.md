# sbatch Flags and Best Practices

**When to use:** User asks about sbatch options, how to write job scripts, or best practices for job submission.

## Essential Flags
| Flag | Purpose | Example |
|------|---------|---------|
| `-J` / `--job-name` | Name the job | `--job-name=train_v2` |
| `-p` / `--partition` | Target partition | `--partition=gpu` |
| `-N` / `--nodes` | Number of nodes | `--nodes=2` |
| `-n` / `--ntasks` | Total MPI tasks | `--ntasks=8` |
| `-c` / `--cpus-per-task` | CPUs per task | `--cpus-per-task=4` |
| `--mem` | Total memory | `--mem=32G` |
| `--mem-per-cpu` | Memory per CPU | `--mem-per-cpu=4G` |
| `-t` / `--time` | Walltime limit | `--time=12:00:00` |
| `--gres` | Generic resources | `--gres=gpu:2` |
| `-o` / `--output` | Stdout file | `--output=logs/%j.out` |
| `-e` / `--error` | Stderr file | `--error=logs/%j.err` |
| `-A` / `--account` | Billing account | `--account=mygroup` |
| `--mail-type` | Email alerts | `--mail-type=END,FAIL` |
| `--mail-user` | Email address | `--mail-user=alice@uni.edu` |

## Advanced Flags
| Flag | Purpose | Example |
|------|---------|---------|
| `--array` | Job arrays | `--array=0-99%10` |
| `--dependency` | Job chains | `--dependency=afterok:12345` |
| `--begin` | Deferred start | `--begin=2024-01-15T08:00` |
| `--deadline` | Must start before | `--deadline=2024-01-16T00:00` |
| `--exclusive` | Whole node | `--exclusive` |
| `--requeue` | Auto-requeue on failure | `--requeue` |
| `--signal` | Signal before timeout | `--signal=B:USR1@120` (2min warning) |
| `--constraint` | Node features | `--constraint=a100` |
| `--nodelist` | Specific nodes | `--nodelist=gpu01,gpu02` |
| `--exclude` | Exclude nodes | `--exclude=gpu03` |
| `--export` | Environment vars | `--export=ALL` or `--export=NONE` |
| `--nice` | Adjust priority | `--nice=100` (lower priority) |
| `--qos` | Quality of service | `--qos=high` |
| `--licenses` | Software licenses | `--licenses=matlab:1` |
| `--tmp` | Temp disk space | `--tmp=100G` |
| `--open-mode` | Append/truncate logs | `--open-mode=append` |
| `--parsable` | Machine-readable output | Returns just job ID |
| `--wrap` | Inline command | `--wrap="hostname"` |

## Output Filename Patterns
- `%j` — job ID
- `%A` — array parent job ID  
- `%a` — array task ID
- `%N` — short hostname
- `%x` — job name
- `%u` — username

## Best Practices
1. Always set explicit `--time`, `--mem`, and `--cpus-per-task` (don't rely on defaults).
2. Use `--output` and `--error` with `%j` to avoid overwriting.
3. Start scripts with `set -euo pipefail` to catch errors early.
4. Use `module purge && module load ...` for reproducibility.
5. For long jobs, add `--signal=B:USR1@300` and trap USR1 for checkpointing.
6. Use `--requeue` if your job can be safely restarted.
7. Set `--mail-type=FAIL` to get notified of failures.

## Template
```bash
#!/bin/bash
#SBATCH --job-name=my_job
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --gres=gpu:1
#SBATCH --time=08:00:00
#SBATCH --output=logs/%j.out
#SBATCH --error=logs/%j.err
#SBATCH --mail-type=END,FAIL

set -euo pipefail
module purge
module load cuda/12.0 python/3.11

echo "Job $SLURM_JOB_ID on $(hostname) at $(date)"
python train.py
echo "Done at $(date)"
```

## Output Format
Show the relevant flags and examples for the user's use case.
