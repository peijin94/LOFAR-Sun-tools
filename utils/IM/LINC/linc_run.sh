#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=256
#SBATCH -J calibration
#SBATCH --mem=250G
#SBATCH --partition=cn

source /home/pjer1316/conda_start.sh

cwltool --singularity --parallel \
	--basedir /discofs/pjer1316/E20230520/ \
       --outdir /discofs/pjer1316/E20230520/results/ \
       --log-dir /discofs/pjer1316/E20230520/logs/ \
       --leave-tmpdir \
       --tmpdir-prefix /discofs/pjer1316/E20230520/run_hba_calibrator/ \
       /discofs/pjer1316/E20230520/lincSun/workflow/calibrator_sun.cwl calibspp.json
