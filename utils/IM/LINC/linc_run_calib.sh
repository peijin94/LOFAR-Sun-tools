#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=20
#SBATCH -J LcalibPJ
#SBATCH --account=project_2008326
#SBATCH --mem=128G
#SBATCH --partition=small
#SBATCH --time=23:59:00
#SBATCH --mail-user=peijin.zhang@helsinki.fi

#source /home/pjer1316/conda_start.sh
#source /projappl/project_2008326/linc_proj/bin/activate

mytmpdir=/dev/shm/run_hba_calibrator/
export SINGULARITY_TMPDIR=$mytmpdir
export TMPDIR=$mytmpdir
export TEMP=$mytmpdir
export TMP=$mytmpdir

alias python=python3

singularity exec -B /scratch/project_2008326/ -B $PWD \
       /scratch/project_2008326/linc_latest.sif \
       cwltool  --no-container --verbose \
	--basedir /scratch/project_2008326/ \
       --outdir /scratch/project_2008326/peijin/E20220523/results/ \
       --log-dir /scratch/project_2008326/peijin/E20220523/logs/ \
       --tmpdir-prefix $mytmpdir \
       /scratch/project_2008326/peijin/lincSun/workflow/calibrator_sun.cwl \
       /scratch/project_2008326/peijin/E20220523/calibLBA.json
