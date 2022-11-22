Interferometry 
======================

Download or Stage data (.MS file)
---------------------------------

The LOFAR data is stored at `LTA <https://lta.lofar.eu/Lofar>`__

Request the data then download the data with **wget**

Preprocess
----------

If the data is raw-data (not processed by pipeline), it is necessary to do the 
autoweight step:

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

In practical:

-  Create the source.db file with a sky model of the calibrator

.. code:: bash

   makesourcedb in=/path/to/TauA.skymodel out=TauA.sourcedb

-  Run auto-weight with NDPPP (Note: this step should be done for both
   sun and the calibrator):

.. code:: bash

   NDPPP msin=/path/to/calibrator.MS
   msout=/path/to/calibrator-autow.MS
   steps=[]

   msin.autoweight=True

-  Use the observation of the calibrator to predict the parameters for
   the calculation applied to the solar observation

.. code:: bash

   NDPPP msin=/path2/to/calibrator-autow.ms \
   Msout=. \
   steps=[gaincal] \
   gaincal.usebeammodel=True  \
   gaincal.solint=4 \
   gaincal.sources=TauAGG \
   gaincal.sourcedb=TauA.sourcedb \
   gaincal.onebeamperpatch=True \
   gaincal.caltype=diagonal

-  Apply the parameters predicted by step (3)

.. code:: bash

   NDPPP msin=/path2/to/sun-autow.ms \
   msout=. \
   msin.datacolumn=DATA \
   msout.datacolumn=CORR_NO_BEAM \
   steps=[applycal] \
   applycal.parmdb=/path/to/calibrator-autow.MS/instrument \
   applycal.updateweights=True

-  Apply the beam model of the calculation for the LOFAR station:

.. code:: bash

   NDPPP msin=sun-autow.MS \
   msout=. \
   msin.datacolumn=CORR_NO_BEAM \
   msout.datacolumn=CORRECTED_DATA \
   steps =[applybeam] \
   applybeam.updateweights=True

The steps (2)-(5) are integrated in the script **auto_sun_calib.py** to
calibrate the MS files in batch.


These steps can be done with a script
`auto_sun_calib.py <https://github.com/peijin94/LOFAR-Sun-tools/blob/master/utils/IM/auto_sun_calib.py>`__, the script
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

An example of wsclean for the sun:


.. code:: bash

   wsclean -j 40 -mem 30 -no-reorder -no-update-model-required \
   -mgain 0.3 -weight briggs 0 -size 512 512 \
   -scale 10asec -pol I -data-column CORRECTED_DATA \
   -niter 1000 -intervals-out 1 -interval 10 11 \
   -name /path/to/prefix \
   /path/to/sun-autow.MS


it is better to
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
|        |        | memory. (Don't use 100%)                           |
+--------+--------+----------------------------------------------------+
| -weight| briggs | Weight for the baselines. (Briggs 0 works for most |
|        | 0.2    | of the situations)                                 |
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
unit of Jy/Beam, the module *lofarSun.IM* can transform the
coordinate to heliocentric frame and convert the flux to brightness
temperature distribution according to the equation given in the Equation
given in `Flux
intensity <https://science.nrao.edu/facilities/vla/proposing/TBconv>`__.

A demo of visualizing lofar interferometry :
`demo <https://github.com/peijin94/LOFAR-Sun-tools/tree/master/demo>`__

For the use of jupyterlab in CEP3, we need to jump from portal to compute

.. code:: bash

   ssh -L 1234:localhost:1234 username@portal.lofar.eu -t ssh -L 1234:localhost:1234 username@lhd001 -t ssh -L 1234:localhost:1234 username@lof001

   source /data/scratch/zhang/conda_start.sh

   python -m jupyter notebook --no-browser --port=1234

Change username and 1234 accordingly.
