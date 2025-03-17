#!/bin/bash

#PBS -P gpu
#PBS -N test
#PBS -o output.log
#PBS -e error.log
#PBS -q gpu
#PBS -l ngpus=1
#PBS -l ncpus=8

module load scientific/pytorch/2.0.0-ngc
cd ${PBS_O_WORKDIR:-""}

export IMAGE_PATH=hf_3.sif
export PYTHONUNBUFFERED=1
export HF_HOME="$HOME/.cache/huggingface"  # Ensure writable cache directory
export TRANSFORMERS_OFFLINE=1              # Ensure offline mode

# Run the script using Apptainer
apptainer exec --nv hf_3.sif python3 hf_3.py