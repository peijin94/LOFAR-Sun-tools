
export TOIL_SLURM_ARGS='-N 1' 
export TOIL_SLURM_PE='cn'
toil-cwl-runner --batchSystem slurm \
       --singularity \
	--workDir  /discofs/pjer1316/E20230520/ \
       --jobStore /discofs/pjer1316/E20230520/JobStore/ \
       --logFile /discofs/pjer1316/E20230520/Linc-L628614.log \
       --outdir /discofs/pjer1316/E20230520/resultsToil/ \
       --log-dir /discofs/pjer1316/E20230520/logs/ \
       --tmpdir-prefix /discofs/pjer1316/E20230520/run_hba_calibrator/ \
       --maxLogFileSize 20000000000 \
       --stats \
       /discofs/pjer1316/E20230520/lincSun/workflow/calibrator_sun.cwl calibspp.json
