#!/bin/bash
#SBATCH --partition=epyc2
#SBATCH --chdir=/storage/homefs/ch21o450/
#SBATCH --mail-user=chantal.hari@unibe.ch
#SBATCH --mail-type=SUBMIT,END,FAIL
#SBATCH --output=/storage/homefs/ch21o450/logs/03a_luf_SA%A_%a.out
#SBATCH --error=/storage/homefs/ch21o450/logs/03a_luf_SA%A_%a.err
#SBATCH --time=95:59:00
#SBATCH --cpus-per-task=5
#SBATCH --mem=100G

module load Anaconda3
conda activate my_env
module purge 
module load Anaconda3

# Define arrays of taxas and models
TAXAS=("Mammals" "Amphibians" "Bird")
MODELS=("GAM" "GBM")
TIME=(65)

TIME=${TIME[$SLURM_ARRAY_TASK_ID % ${#TIME[@]}]}
TAXA=${TAXAS[$SLURM_ARRAY_TASK_ID / (${#TIME[@]} * ${#MODELS[@]})]}
MODEL=${MODELS[($SLURM_ARRAY_TASK_ID / ${#TIME[@]}) % ${#MODELS[@]}]}


chmod +x /storage/homefs/ch21o450/scripts/climate_Hari_etal_inprep/functions/LUF_calculations/03a_luf_SA_1995_luh2.py

# Pass the arguments to luf.py
python3 /storage/homefs/ch21o450/scripts/climate_Hari_etal_inprep/functions/LUF_calculations/03a_luf_SA_1995_luh2.py -t $TIME -m $MODEL -a $TAXA

