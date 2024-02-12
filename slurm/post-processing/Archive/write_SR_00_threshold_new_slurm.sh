#!/bin/bash
#SBATCH --partition=epyc2
#SBATCH --chdir=/storage/homefs/ch21o450/
#SBATCH --mail-user=chantal.hari@unibe.ch
#SBATCH --mail-type=SUBMIT,END,FAIL
#SBATCH --output=/storage/homefs/ch21o450/logs/calculate_newRS%A_%a.out
#SBATCH --error=/storage/homefs/ch21o450/logs/calculate_newSRsb%A_%a.err
#SBATCH --time=48:00:00
#SBATCH --cpus-per-task=10
#SBATCH --mem=300G

module load Anaconda3

# Define arrays of taxas and models
TAXAS=("Bird")
MODELS=("GAM" "GBM")

# Calculate indices based on SLURM_ARRAY_TASK_ID
taxa_idx=$(($SLURM_ARRAY_TASK_ID % ${#TAXAS[@]}))
model_idx=$(($SLURM_ARRAY_TASK_ID / ${#TAXAS[@]}))

TAXA=${TAXAS[$taxa_idx]}
MODEL=${MODELS[$model_idx]}



chmod +x /storage/homefs/ch21o450/scripts/BioScenComb/functions/post-processing/write_SR_00_threshold_new.py

# Pass the arguments to luf.py
python3 /storage/homefs/ch21o450/scripts/BioScenComb/functions/post-processing/write_SR_00_threshold_new.py -a $TAXA -m $MODEL