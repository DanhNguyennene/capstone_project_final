#!/bin/bash
#SBATCH --job-name=file_processor
#SBATCH --partition=cpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:15:00
#SBATCH --output=logs/fileproc_%j.out
#SBATCH --error=logs/fileproc_%j.err

mkdir -p logs

echo "=== File Processing Job ==="
echo "Job ID:  $SLURM_JOB_ID"
echo "Node:    $SLURMD_NODENAME"
echo "Started: $(date)"

INPUT_DIR="/tmp/batch_input"
OUTPUT_DIR="/tmp/batch_output/$SLURM_JOB_ID"
mkdir -p "$INPUT_DIR" "$OUTPUT_DIR"

# Create sample input files if they don't exist
if [ ! -f "$INPUT_DIR/file_001.csv" ]; then
    echo "Creating sample input files..."
    for i in $(seq -w 1 50); do
        echo "id,value,category" > "$INPUT_DIR/file_${i}.csv"
        for j in $(seq 1 100); do
            echo "${j},$((RANDOM % 1000)),cat_$((RANDOM % 5))" >> "$INPUT_DIR/file_${i}.csv"
        done
    done
fi

# Process each file
TOTAL=$(ls "$INPUT_DIR"/*.csv 2>/dev/null | wc -l)
DONE=0

for f in "$INPUT_DIR"/*.csv; do
    base=$(basename "$f")
    # Simple aggregation: count lines, sum values
    python3 -c "
import csv, pathlib, json
data = list(csv.DictReader(open('$f')))
result = {
    'file': '$base',
    'rows': len(data),
    'sum_value': sum(int(r['value']) for r in data),
    'categories': len(set(r['category'] for r in data))
}
pathlib.Path('$OUTPUT_DIR/${base%.csv}_result.json').write_text(json.dumps(result))
"
    DONE=$((DONE + 1))
    if (( DONE % 10 == 0 )); then
        echo "Processed $DONE/$TOTAL files"
    fi
done

echo "All $TOTAL files processed → $OUTPUT_DIR"
echo "Finished: $(date)"
