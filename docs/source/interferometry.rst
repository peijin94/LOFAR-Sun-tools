Interferometry Imaging
======================

Download or Stage data (.MS file)
---------------------------------

The LOFAR data is stored at `LTA <https://lta.lofar.eu/Lofar>`__

Request the data then download the data with **wget**

Preprocess
----------

If the data is un-calibrated data, do use the NDPPP to auto weight the
data set:

.. code:: bash

   NDPPP msin=path/to/rawdata.MS msout=path/to/output.MS steps=[] msin.autoweight=true

The script autoWeight.sh can batch this process if there is more than
one file

(This step can be skipped if the measurement set has been calibrated.)

Calibration
-----------

The calibration depends on NDPPP module developed by LOFAR, so run this
line before everything:

.. code:: bash

    module load lofar
    module load dp3

The meassurement set is calibrated with NDPPP in three steps:

-  **Predicted Calculation** : use the calibrator to predict the gain
   calculation
-  **Apply Calculation** : apply the gain calculation to the sun
-  **Apply Beam** : apply the LOFAR beam to the dataset

These steps can be done with a script
`auto_sun_calib.py <../pro/script/auto_sun_calib.py>`__, the script
automized the calibration of interferometry, it generates the parset
file for the calibration and run the corresponding NDPPP commad.

Modify the configuration lines in the code:

.. code:: python

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

Run the calibration script simply with:

.. code:: bash

   python auto_sun_calib.py

Clean
-----

An example of wsclean for the sun
`wsclean_script.sh <../pro/script/wsclean_script.sh>`__, it is better to
keep the parameter **-multiscale** on for the solar image CLEAN, because
the solar radio emission is always extended.

A small cheatsheet for solar wsclean:

+--------+--------+----------------------------------------------------+
| C      | Par    | Comment                                            |
| ommand | ameter |                                                    |
+========+========+====================================================+
| -j     | 20     | Number of thread used for CLEAN. (can be equal to  |
|        |        | the number of cores)                               |
+--------+--------+----------------------------------------------------+
| -mem   | 80     | Maximum memory limit in percent to the system      |
|        |        | memory. (Don’t use 100%)                           |
+--------+--------+----------------------------------------------------+
| -      | briggs | Weight for the baselines. (Briggs 0 works for most |
| weight | 0.2    | of the situations)                                 |
+--------+--------+----------------------------------------------------+
| -size  | 2048   | Size of the image in pixel.                        |
|        | 2048   |                                                    |
+--------+--------+----------------------------------------------------+
| -scale | 3asec  | The scale of one pixel, can be 0.1asec,3asec,      |
|        |        | 3min, 3deg                                         |
+--------+--------+----------------------------------------------------+
| -pol   | I      | The polarization for cleaning, can be I,Q,U,V.     |
+--------+--------+----------------------------------------------------+
| -mult  | \\     | Whether to use multiscale in the clean. Better to  |
| iscale |        | switch on for extended source                      |
+--------+--------+----------------------------------------------------+
| -data- | CO     | Be sure to use the calibrated data                 |
| column | RRECTE | (CORRECTED_DATA)                                   |
|        | D_DATA |                                                    |
+--------+--------+----------------------------------------------------+
| -niter | 2000   | The iteration of clean, for the sun, 400 is        |
|        |        | necessary, 1000 can be better, 2000 is enough.     |
+--------+--------+----------------------------------------------------+
| -i     | 85     | How many images you want to produce                |
| nterva |        |                                                    |
| ls-out |        |                                                    |
+--------+--------+----------------------------------------------------+
| -in    | 3000   | The index range for the CLEAN                      |
| terval | 4000   |                                                    |
+--------+--------+----------------------------------------------------+

for the interval index, one can use the get_datetime_index.py to find
out the starting and ending index

Visualization
-------------

WSClean produces fits image with astronomy coordinate [RA,DEC] and the
unit of Jy/Beam, the module *LofarDataCleaned* in
`lofarData <../pro/src/lofarSun/lofarData.py>`__ can transform the
coordinate to heliocentric frame and convert the flux to brightness
temperature distribution according to the equation given in the Equation
given in `Flux
intensity <https://science.nrao.edu/facilities/vla/proposing/TBconv>`__.

A demo of visualizing lofar interferometry :
`demo <../demo/demo_lofarmap.ipynb>`__

. For the use of jupyterlab in CEP3

.. code:: bash

   ssh -L 1234:localhost:1234 username@portal.lofar.eu -t ssh -L 1234:localhost:1234 username@lhd001 -t ssh -L 1234:localhost:1234 username@lof001

   source /data/scratch/zhang/conda_start.sh

   python -m jupyter notebook --no-browser --port=1234

Change username and 1234 accordingly.
