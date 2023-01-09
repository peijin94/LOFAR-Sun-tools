#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=40
#SBATCH -J LOFAR-calib
#SBATCH --mem=64G
#SBATCH --constraint=avx
#SBATCH --array=0-243
#SBATCH --clusters=kale
#SBATCH --partition=short
#SBATCH --time=03:59:00
#SBATCH --mail-user=peijin.zhang@helsinki.fi


srun singularity exec -B /proj/group/corona/radio/,/wrk/group/corona/ \
    /proj/group/corona/radio/lofar-pipeline.simg \
    bash -c "source /opt/lofarsoft/lofarinit.sh && sleep 1 && time \
    python3 autoCalib_job.py ${SLURM_ARRAY_TASK_ID} && \
    echo 'done' && sleep 1"

