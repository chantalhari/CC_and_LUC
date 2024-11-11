#!/bin/bash
#SBATCH --partition=epyc2
#SBATCH --chdir=/storage/homefs/ch21o450/
#SBATCH --mail-user=chantal.hari@unibe.ch
#SBATCH --mail-type=SUBMIT,END,FAIL
#SBATCH --output=/storage/homefs/ch21o450/logs/05b_luf_hist%A_%a.out
#SBATCH --error=/storage/homefs/ch21o450/logs/05b_luf_hist%A_%a.err
#SBATCH --time=95:59:00
#SBATCH --cpus-per-task=5
#SBATCH --mem=100G

module load Anaconda3
source activate my_env 
module load Anaconda3
# Define arrays of taxas and models
TAXAS=("Amphibians" "Mammals" "Bird")
MODELS=("GAM" "GBM")

# Calculate indices based on SLURM_ARRAY_TASK_ID
TAXA=${TAXAS[$SLURM_ARRAY_TASK_ID / ${#MODELS[@]}]}
MODEL=${MODELS[$SLURM_ARRAY_TASK_ID % ${#MODELS[@]}]}


chmod +x /storage/homefs/ch21o450/scripts/climate_Hari_etal_inprep/functions/LUF_calculations/05b_luf_hist_dispersal4.py

# Pass the arguments to luf.py
python3 /storage/homefs/ch21o450/scripts/climate_Hari_etal_inprep/functions/LUF_calculations/05b_luf_hist_dispersal4.py -m $MODEL -a $TAXA
