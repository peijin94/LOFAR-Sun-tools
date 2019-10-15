# LOFAR Solar
 Handy scripts for the LOFAR solar data processing

## wsclean\_script.sh

An example of wsclean for the sun, it is better to keep the parameter **-multiscale** on for the solar image CLEAN, because the solar radio emission is always extended.

A small cheatsheet for solar wsclean:

| Command        | Parameter      | Comment                                                                                      |
|----------------|----------------|----------------------------------------------------------------------------------------------|
| -j             | 20             | Number of thread used for CLEAN.  (can be equal to the number of cores)                      |
| -mem           | 80             | Maximum memory limit in percent to  the system memory. (Don't use 100%)                      |
| -weight        | briggs 0.2     | Weight for the baselines. (Briggs 0  works for most of the situations)                       |
| -size          | 2048 2048      | Size of the image in pixel.                                                                  |
| -scale         | 3asec          | The scale of one pixel, can be  0.1asec,3asec, 3min, 3deg                                    |
| -pol           | I              | The polarization for cleaning,  can be I,Q,U,V.                                              |
| -multiscale    | \              | Whether to use multiscale in the  clean. Better to switch on for  extended source            |
| -data-column   | CORRECTED\_DATA | Be sure to use the calibrated data  (CORRECTED\_DATA)                                       |
| -niter         | 2000           | The iteration of clean, for the sun,  400 is necessary, 1000 can be better,  2000 is enough. |
| -intervals-out | 85             | How many images you want to produce                                                          |
| -interval      | 3000 4000      | The index range for the CLEAN                                                                |

for the interval index, one can use the get\_datetime\_index.py to find out the starting and ending index


## auto\_sun\_calib.py

 This script automized the calibration of interferometry, it generates the parset file for the calibration and run the corresponding NDPPP commad.

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


## LOFAR\_h5\_to\_fits.py

To convert huge HDF5 file to a bunch of small fits file with json and quickview png


## display\_lofar\_sun(\_py37).py

To transform the coordinate of RA,DEC into the heliocentric coordinate for the plot

## Quick View the LOFAR beamform

[QuickView](src\BeamformedQuickView\README.md)

![demo](https://raw.githubusercontent.com/Pjer-zhang/LOFAR_Solar/master/src/img/demo.gif)