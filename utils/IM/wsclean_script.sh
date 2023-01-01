wsclean -j 40 -mem 80 -no-reorder -no-update-model-required \
	-mgain 0.7 -weight briggs 0.2 -size 2048 2048 \
	-scale 3asec -pol I -auto-mask 5 -multiscale \
	-auto-threshold 1 -data-column CORRECTED_DATA \
	-niter 2000 -intervals-out 85 -interval 6995 7080 \
	-fit-beam -make-psf -name name-of-output 
	/path/to/inputfile.MS
