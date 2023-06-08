wsclean -j 40 -mem 80  -no-reorder -no-update-model-required \
     -mgain 0.7 -weight briggs 0 -multiscale \
     -auto-mask 3 -auto-threshold 0.3   \
     -size 500 500 -scale 30asec  -pol I -data-column CORRECTED_DATA \
     -niter 3000 -intervals-out 100 -interval  200 301 \
     -fit-beam -name fits/SB020 MS_aw/L698487_SAP000_SB020_uv.MS

#wsclean -j 40 -mem 80 -no-reorder -no-update-model-required \
#	-mgain 0.7 -weight briggs 0.2 -size 2048 2048 \
#	-scale 3asec -pol I -auto-mask 5 -multiscale \
#	-auto-threshold 1 -data-column CORRECTED_DATA \
#	-niter 2000 -intervals-out 85 -interval 6995 7080 \
#	-fit-beam -make-psf -name name-of-output 
#	/path/to/inputfile.MS



