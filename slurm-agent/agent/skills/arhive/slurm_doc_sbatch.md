# Slurm Official: sbatch

**When to use:** User asks about job submission, dependencies, arrays, partitions, or GPU flags.
**Official source:** https://slurm.schedmd.com/sbatch.html
**Refreshed:** 2026-04-19 04:03:51 UTC

## Fast Path
- Use sbatch for non-interactive batch submission.
- Use --dependency for ordering; do not wait-loop before submission.
- Use --array for parallel task indices and --gres for GPU allocation.

## Canonical Examples
```bash
sbatch train.sh
sbatch --dependency=afterok:1004 evaluate.sh
sbatch --partition=gpu --gres=gpu:2 train_gpu.sh
sbatch --array=1-10 hyperparam_sweep.sh
```

## Retrieved Notes
- Slurm Workload Manager - sbatch
- sbatch
- sbatch - Submit a batch script to Slurm.
- sbatch [ OPTIONS(0) ...] [ : [ OPTIONS(N) ...]] script(0) [ args(0) ...]
- sbatch submits a batch script to Slurm. The batch script may be given to
- sbatch through a file name on the command line, or if no file name is specified,
- sbatch will read in a script from standard input.
- The batch script may contain one or more lines beginning with "#SBATCH" followed
- by any of the CLI options documented on this page. #SBATCH directives are read
- reached in the script, no more #SBATCH directives will be processed. See example
- sbatch exits immediately after the script is successfully transferred to the
- sbatch will return 0 on success or error code on failure.

## Agent Usage
- Use these patterns as primary guidance for command selection and flags.
- If needed, run web_search with: site:slurm.schedmd.com <topic>.
