#!/bin/bash
#SBATCH --job-name=health_check
#SBATCH --partition=debug
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=00:05:00
#SBATCH --output=logs/health_%j.out
#SBATCH --error=logs/health_%j.err

mkdir -p logs

LOGFILE="/tmp/health_$(date +%Y%m%d_%H%M%S).log"

echo "=== Cluster Health Check ===" | tee "$LOGFILE"
echo "Timestamp: $(date -Iseconds)"  | tee -a "$LOGFILE"
echo ""                               | tee -a "$LOGFILE"

echo "--- Node States ---"            | tee -a "$LOGFILE"
sinfo -N -l 2>/dev/null               | tee -a "$LOGFILE"
echo ""                               | tee -a "$LOGFILE"

echo "--- Queue Summary ---"          | tee -a "$LOGFILE"
squeue -h -o "%.8T" | sort | uniq -c  | tee -a "$LOGFILE"
echo ""                               | tee -a "$LOGFILE"

echo "--- Partition Status ---"        | tee -a "$LOGFILE"
sinfo -o "%P %a %D %C %G" 2>/dev/null | tee -a "$LOGFILE"
echo ""                               | tee -a "$LOGFILE"

echo "--- Disk Usage ---"             | tee -a "$LOGFILE"
df -h /tmp /home 2>/dev/null          | tee -a "$LOGFILE"
echo ""                               | tee -a "$LOGFILE"

echo "--- Load Average ---"           | tee -a "$LOGFILE"
uptime                                | tee -a "$LOGFILE"

echo ""                               | tee -a "$LOGFILE"
echo "Health log written to: $LOGFILE" | tee -a "$LOGFILE"
