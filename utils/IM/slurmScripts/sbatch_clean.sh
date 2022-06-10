#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=256
#SBATCH -J clean
#SBATCH --mem=250G
#SBATCH --array=0-59


srun singularity run -B /discofs/pjer1316/ ~/lofar-pipeline.simg ./runOneJob.sh 'python3 clean_job.py' ${SLURM_ARRAY_TASK_ID}
