#!/bin/bash
#SBATCH --job-name=backup_cleanup
#SBATCH --partition=debug
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:10:00
#SBATCH --output=logs/backup_%j.out
#SBATCH --error=logs/backup_%j.err

mkdir -p logs

echo "=== Backup & Cleanup Job ==="
echo "Job ID:  $SLURM_JOB_ID"
echo "Node:    $SLURMD_NODENAME"
echo "Started: $(date)"

WORK_DIR="/tmp/ml_pipeline"
BACKUP_DIR="/tmp/backups/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# Backup results if they exist
if [ -d "$WORK_DIR" ]; then
    echo "Backing up $WORK_DIR → $BACKUP_DIR/"
    cp -r "$WORK_DIR" "$BACKUP_DIR/" 2>/dev/null || echo "  (nothing to back up)"
    
    # Report sizes
    echo ""
    echo "Backup contents:"
    du -sh "$BACKUP_DIR"/* 2>/dev/null || echo "  (empty)"
else
    echo "No work directory found at $WORK_DIR"
fi

# Clean up old temp files (> 7 days)
echo ""
echo "Cleaning temp files older than 7 days..."
find /tmp/sim_checkpoints /tmp/batch_output /tmp/ml_pipeline -maxdepth 1 -mtime +7 -exec rm -rf {} \; 2>/dev/null
echo "Cleanup done."

echo ""
echo "Disk usage after cleanup:"
df -h /tmp

echo "Finished: $(date)"
