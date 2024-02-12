#!/bin/bash
#SBATCH --partition=epyc2
#SBATCH --chdir=/storage/homefs/ch21o450/
#SBATCH --mail-user=chantal.hari@unibe.ch
#SBATCH --mail-type=SUBMIT,END,FAIL
#SBATCH --output=/storage/homefs/ch21o450/logs/habitat_barplots_loss%A_%a.out
#SBATCH --error=/storage/homefs/ch21o450/logs/habitat_barplotsSR_loss%A_%a.err
#SBATCH --time=95:59:00
#SBATCH --cpus-per-task=10
#SBATCH --mem=300G

module load Anaconda3

TIMES=(35 65)
SCENARIOS=("rcp26" "rcp60")

# Calculate indices based on SLURM_ARRAY_TASK_ID
TIME=${TIMES[$SLURM_ARRAY_TASK_ID / ${#SCENARIOS[@]}]}
SCENARIO=${SCENARIOS[$SLURM_ARRAY_TASK_ID % ${#SCENARIOS[@]}]}


chmod +x /storage/homefs/ch21o450/scripts/BioScenComb/functions/post-processing/barplots_loss_habitat.py

# Pass the arguments to luf.py
python3 /storage/homefs/ch21o450/scripts/BioScenComb/functions/post-processing/barplots_loss_habitat.py  -m $SCENARIO -a $TIME

