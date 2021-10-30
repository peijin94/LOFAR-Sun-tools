wsclean -j 40 -mem 80  -no-reorder -no-update-model-required \
     -mgain 0.7 -weight briggs 0 -multiscale \
     -auto-mask 3 -auto-threshold 0.3   \
     -size 500 500 -scale 30asec  -pol I -data-column CORRECTED_DATA \
     -niter 3000 -intervals-out 100 -interval  200 301 \
     -fit-beam -name fits/SB020 MS_aw/L698487_SAP000_SB020_uv.MS


