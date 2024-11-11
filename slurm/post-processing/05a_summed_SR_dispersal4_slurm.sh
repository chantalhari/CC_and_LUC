#!/bin/bash
#SBATCH --partition=epyc2
#SBATCH --chdir=/storage/homefs/ch21o450/
#SBATCH --mail-user=chantal.hari@unibe.ch
#SBATCH --mail-type=SUBMIT,END,FAIL
#SBATCH --output=/storage/homefs/ch21o450/logs/05a_summed_SR_dispersal4%A_%a.out
#SBATCH --error=/storage/homefs/ch21o450/logs/05a_summed_SR_dispersal4%A_%a.err
#SBATCH --time=12:59:00
#SBATCH --cpus-per-task=5
#SBATCH --mem=300G

module load Anaconda3
source activate my_env 
module load Anaconda3


TIMES=(35 65)
SCENARIOS=("rcp26" "rcp60")

# Calculate indices based on SLURM_ARRAY_TASK_ID
TIME=${TIMES[$SLURM_ARRAY_TASK_ID / ${#SCENARIOS[@]}]}
SCENARIO=${SCENARIOS[$SLURM_ARRAY_TASK_ID % ${#SCENARIOS[@]}]}


chmod +x /storage/homefs/ch21o450/scripts/climate_Hari_etal_inprep/functions/post-processing/05a_summed_SR_dispersal4.py

# Pass the arguments to luf.py
python3 /storage/homefs/ch21o450/scripts/climate_Hari_etal_inprep/functions/post-processing/05a_summed_SR_dispersal4.py  -m $SCENARIO -a $TIME

