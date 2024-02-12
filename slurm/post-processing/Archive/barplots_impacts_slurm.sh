#!/bin/bash
#SBATCH --partition=epyc2
#SBATCH --chdir=/storage/homefs/ch21o450/
#SBATCH --mail-user=chantal.hari@unibe.ch
#SBATCH --mail-type=SUBMIT,END,FAIL
#SBATCH --output=/storage/homefs/ch21o450/logs/barplos%A_%a.out
#SBATCH --error=/storage/homefs/ch21o450/logs/barplots%A_%a.err
#SBATCH --time=95:59:00
#SBATCH --cpus-per-task=10
#SBATCH --mem=200G

module load Anaconda3



chmod +x /storage/homefs/ch21o450/scripts/BioScenComb/functions/post-processing/barplots_impact.py

# Pass the arguments to luf.py
python3 /storage/homefs/ch21o450/scripts/BioScenComb/functions/post-processing/barplots_impact.py 
