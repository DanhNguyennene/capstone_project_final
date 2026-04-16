#!/bin/bash
#SBATCH --job-name=ml_evaluate
#SBATCH --partition=gpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --gres=gpu:1
#SBATCH --time=00:30:00
#SBATCH --output=logs/evaluate_%j.out
#SBATCH --error=logs/evaluate_%j.err
# NOTE: submit with --dependency=afterok:<train_gpu_job_id>

set -euo pipefail

PROCESSED_DIR="${SCRATCH:-/tmp}/ml_pipeline/processed"
MODEL_DIR="${SCRATCH:-/tmp}/ml_pipeline/model"
RESULTS_DIR="${SCRATCH:-/tmp}/ml_pipeline/results"
mkdir -p "$RESULTS_DIR" logs

echo "=== Stage 4: Evaluation ==="
echo "Job ID:  $SLURM_JOB_ID"
echo "Node:    $SLURMD_NODENAME"
echo "GPUs:    ${CUDA_VISIBLE_DEVICES:-none (no GRES configured)}"
echo "Started: $(date)"

# ── Guard ─────────────────────────────────────────────────────────────────────
if [[ ! -f "$MODEL_DIR/.train_complete" ]]; then
    echo "ERROR: Training sentinel not found in $MODEL_DIR" >&2
    exit 1
fi

# ── Evaluate ──────────────────────────────────────────────────────────────────
CHECKPOINT="${CHECKPOINT:-best_model.pt}"

echo "Loading checkpoint: $MODEL_DIR/$CHECKPOINT"
echo "Running evaluation on test split ..."

python3 - <<PYEOF
import os, json, pathlib, random

model_dir   = pathlib.Path(os.environ["MODEL_DIR"])
processed   = pathlib.Path(os.environ["PROCESSED_DIR"])
results_dir = pathlib.Path(os.environ["RESULTS_DIR"])
checkpoint  = os.environ.get("CHECKPOINT", "best_model.pt")

# Load checkpoint meta
ckpt = json.loads((model_dir / checkpoint).read_text())
print(f"  Checkpoint epoch: {ckpt.get('epoch', '?')}  "
      f"val_loss: {ckpt.get('val_loss', '?'):.4f}")

# Simulated test evaluation (replace with your real inference loop)
random.seed(99)
n_samples = max(1, len(list((processed / "test").glob("*.sample"))))

results = {
    "checkpoint":  checkpoint,
    "n_samples":   n_samples,
    "accuracy":    round(random.uniform(0.85, 0.97), 4),
    "precision":   round(random.uniform(0.84, 0.96), 4),
    "recall":      round(random.uniform(0.83, 0.96), 4),
    "f1":          round(random.uniform(0.84, 0.96), 4),
    "test_loss":   round(random.uniform(0.08, 0.25), 4),
}
results["f1"] = round(
    2 * results["precision"] * results["recall"]
      / (results["precision"] + results["recall"] + 1e-9), 4
)

print()
print("Test results:")
print(f"  Samples   : {results['n_samples']}")
print(f"  Accuracy  : {results['accuracy']:.4f}")
print(f"  Precision : {results['precision']:.4f}")
print(f"  Recall    : {results['recall']:.4f}")
print(f"  F1        : {results['f1']:.4f}")
print(f"  Test loss : {results['test_loss']:.4f}")

report_path = results_dir / "evaluation_report.json"
report_path.write_text(json.dumps(results, indent=2))
print(f"\nReport written to {report_path}")
PYEOF

echo "$SLURM_JOB_ID $(date -Iseconds)" > "$RESULTS_DIR/.eval_complete"
echo "Finished: $(date)"
