# LOFAR Solar
 Handy scripts for the LOFAR solar data processing

## auto\_sun\_calib.py

This script automized the calibration of interferometry, it generates the parset file for the calibration and run the corresponding commad.

#### Usage

The calibration depends on NDPPP module developed by LOFAR, so run this line before everything:

```bash
module load lofar
```

Revice the configuration lines in the code:
```python
sources  = 'TauAGG'  # source type
sourcedb = 'taurus_1.sourcedb' # path to the source

sun_MS_dir   = 'MS/' # path to the dir contain sun's MS 
calib_MS_dir = 'MS/' # path to the dir contain calibrator's MS

obs_id_sun   = 'L722384' # obsid of the sun
obs_id_calib = 'L701915' # obsid of the calibrator

idx_range_sun  = [32,39] # index range of the subband of the Sun
idx_range_cali = [92,99] # index range of the subband of the Sun

run_step = [0,1,2]; # 0 for predict; 1 for applycal;  2 for applybeam
		# [0,1,2] for complete calibration
```

Run the code simply  with:

```bash
python auto_sun_calib.py
```
