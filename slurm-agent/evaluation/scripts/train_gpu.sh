#!/bin/bash
#SBATCH --job-name=ml_train_gpu
#SBATCH --partition=gpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --gres=gpu:1
#SBATCH --time=01:00:00
#SBATCH --output=logs/train_gpu_%j.out
#SBATCH --error=logs/train_gpu_%j.err
# NOTE: submit with --dependency=afterok:<preprocess_job_id>

set -euo pipefail

PROCESSED_DIR="${SCRATCH:-/tmp}/ml_pipeline/processed"
MODEL_DIR="${SCRATCH:-/tmp}/ml_pipeline/model"
mkdir -p "$MODEL_DIR" logs

echo "=== Stage 3: GPU Training ==="
echo "Job ID:    $SLURM_JOB_ID"
echo "Node:      $SLURMD_NODENAME"
echo "GPUs:      ${CUDA_VISIBLE_DEVICES:-none (no GRES configured)}"
echo "CPUs:      $SLURM_CPUS_PER_TASK"
echo "Memory:    ${SLURM_MEM_PER_NODE}MB"
echo "Started:   $(date)"

# ── Guard ─────────────────────────────────────────────────────────────────────
if [[ ! -f "$PROCESSED_DIR/.preprocess_complete" ]]; then
    echo "ERROR: Preprocessing sentinel not found in $PROCESSED_DIR" >&2
    exit 1
fi

# ── Environment ───────────────────────────────────────────────────────────────
# Activate your conda / venv here if needed:
# source "$HOME/miniconda3/etc/profile.d/conda.sh" && conda activate ml_env

# ── GPU check ─────────────────────────────────────────────────────────────────
echo "GPU info:"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>/dev/null \
    || echo "  (nvidia-smi unavailable — running in test mode)"

# ── Training ──────────────────────────────────────────────────────────────────
EPOCHS="${EPOCHS:-50}"
LR="${LR:-0.001}"
BATCH="${BATCH_SIZE:-64}"

echo "Hyperparameters: epochs=$EPOCHS lr=$LR batch=$BATCH"
echo "Starting training loop ..."

python3 - <<PYEOF
import os, json, pathlib, time, random

processed = pathlib.Path(os.environ["PROCESSED_DIR"])
model_dir = pathlib.Path(os.environ["MODEL_DIR"])
epochs    = int(os.environ.get("EPOCHS", 50))
lr        = float(os.environ.get("LR", 0.001))
batch     = int(os.environ.get("BATCH_SIZE", 64))

# ── Lightweight training stub (replace with your real training code) ──────────
history = []
best_val_loss = float("inf")

for epoch in range(1, epochs + 1):
    # Simulated metrics — swap in real model.fit() / train loop
    train_loss = max(0.05, 2.0 * (0.92 ** epoch) + random.gauss(0, 0.01))
    val_loss   = max(0.06, 2.1 * (0.91 ** epoch) + random.gauss(0, 0.02))
    val_acc    = min(0.99, 0.5 + 0.48 * (1 - 0.91 ** epoch) + random.gauss(0, 0.005))
    history.append({"epoch": epoch, "train_loss": train_loss,
                    "val_loss": val_loss, "val_acc": val_acc})

    if epoch % 10 == 0 or epoch == 1:
        print(f"  Epoch {epoch:3d}/{epochs}  "
              f"train_loss={train_loss:.4f}  "
              f"val_loss={val_loss:.4f}  "
              f"val_acc={val_acc:.4f}")

    if val_loss < best_val_loss:
        best_val_loss = val_loss
        (model_dir / "best_model.pt").write_text(
            json.dumps({"epoch": epoch, "val_loss": val_loss, "lr": lr}))

# Save full history and final checkpoint
(model_dir / "training_history.json").write_text(json.dumps(history, indent=2))
(model_dir / "final_model.pt").write_text(
    json.dumps({"epochs": epochs, "best_val_loss": best_val_loss}))

print(f"Best val_loss: {best_val_loss:.4f}  (saved to best_model.pt)")
PYEOF

echo "$SLURM_JOB_ID $(date -Iseconds)" > "$MODEL_DIR/.train_complete"
echo "Model artifacts in $MODEL_DIR:"
ls -lh "$MODEL_DIR"
echo "Finished: $(date)"
