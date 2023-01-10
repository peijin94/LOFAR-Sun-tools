#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=40
#SBATCH -J LOFAR-calib
#SBATCH --mem=64G
#SBATCH --constraint=avx
#SBATCH --array=0-243
#SBATCH --clusters=kale
#SBATCH --partition=short
#SBATCH --time=05:59:00
#SBATCH --mail-user=peijin.zhang@helsinki.fi


srun singularity run -B /discofs/pjer1316/ ~/lofar-pipeline.simg ./runOneJob.sh 'python3 clean_job.py' ${SLURM_ARRAY_TASK_ID}
