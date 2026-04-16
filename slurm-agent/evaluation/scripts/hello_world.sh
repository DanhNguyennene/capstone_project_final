#!/bin/bash
#SBATCH --job-name=hello_world
#SBATCH --partition=debug
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=00:05:00
#SBATCH --output=logs/hello_%j.out
#SBATCH --error=logs/hello_%j.err

mkdir -p logs
echo "Hello from Slurm!"
echo "Job ID:    $SLURM_JOB_ID"
echo "Node:      $SLURMD_NODENAME"
echo "Partition: $SLURM_JOB_PARTITION"
echo "CPUs:      $SLURM_CPUS_ON_NODE"
echo "Memory:    ${SLURM_MEM_PER_NODE:-N/A}MB"
echo "Time:      $(date)"
hostname
sleep 2
echo "Done!"
