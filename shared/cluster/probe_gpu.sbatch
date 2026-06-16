#!/bin/bash
#SBATCH --job-name=probe_gpu
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --time=00:05:00
#SBATCH --output=logs/probe_gpu_%j.out
#SBATCH --error=logs/probe_gpu_%j.err

echo "HOSTNAME=$(hostname)"
echo "USER=$(whoami)"
echo "PWD=$(pwd)"
echo "DATE=$(date)"
echo ""
echo "=== NVIDIA SMI ==="
nvidia-smi
echo ""
echo "=== GPU QUERY ==="
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
