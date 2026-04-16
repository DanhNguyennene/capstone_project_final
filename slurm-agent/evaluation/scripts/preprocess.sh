#!/bin/bash
#SBATCH --job-name=ml_preprocess
#SBATCH --partition=cpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=00:30:00
#SBATCH --output=logs/preprocess_%j.out
#SBATCH --error=logs/preprocess_%j.err
# NOTE: submit with --dependency=afterok:<data_download_job_id>

set -euo pipefail

DATASET_DIR="${SCRATCH:-/tmp}/ml_pipeline/dataset"
PROCESSED_DIR="${SCRATCH:-/tmp}/ml_pipeline/processed"
mkdir -p "$PROCESSED_DIR" logs

echo "=== Stage 2: Preprocessing ==="
echo "Job ID:  $SLURM_JOB_ID"
echo "Node:    $SLURMD_NODENAME"
echo "CPUs:    $SLURM_CPUS_PER_TASK"
echo "Started: $(date)"

# ── Guard: upstream stage must have completed ─────────────────────────────────
if [[ ! -f "$DATASET_DIR/.download_complete" ]]; then
    echo "ERROR: $DATASET_DIR/.download_complete not found." >&2
    echo "Run data_download.sh first (or use --dependency=afterok)." >&2
    exit 1
fi

# ── Preprocessing steps ───────────────────────────────────────────────────────
echo "Splitting into train/val/test (80/10/10) ..."
python3 - <<'PYEOF'
import os, pathlib, random, shutil

src  = pathlib.Path(os.environ["DATASET_DIR"])
dest = pathlib.Path(os.environ["PROCESSED_DIR"])
random.seed(42)

files = sorted(src.glob("*.sample"))  # adjust glob for your dataset format
random.shuffle(files)

n       = len(files)
n_train = int(0.8 * n)
n_val   = int(0.1 * n)

splits = {
    "train": files[:n_train],
    "val":   files[n_train:n_train + n_val],
    "test":  files[n_train + n_val:],
}

for split, split_files in splits.items():
    split_dir = dest / split
    split_dir.mkdir(parents=True, exist_ok=True)
    for f in split_files:
        shutil.copy(f, split_dir / f.name)
    print(f"  {split}: {len(split_files)} samples")
PYEOF

echo "Normalising features ..."
python3 - <<'PYEOF'
import os, pathlib, json

processed = pathlib.Path(os.environ["PROCESSED_DIR"])
stats = {"mean": 0.0, "std": 1.0, "n_samples": 0}  # placeholder

for split in ("train", "val", "test"):
    samples = list((processed / split).glob("*.sample"))
    stats["n_samples"] += len(samples)

(processed / "stats.json").write_text(json.dumps(stats, indent=2))
print(f"  stats.json written — {stats['n_samples']} total samples")
PYEOF

echo "$SLURM_JOB_ID $(date -Iseconds)" > "$PROCESSED_DIR/.preprocess_complete"

echo "Finished: $(date)"
