======================
Interferometry 
======================


Download
----------

LOFAR observation data are available at the
`Long Term Archive (LTA) <https://lta.lofar.eu/Lofar>`__.
The LTA is difficult to navigate and thus, we recommend reading the
`Long Term Archive Howto <https://www.astron.nl/lofarwiki/doku.php?id=public:lta_howto>`__
on the LOFAR wiki.

**Note** :
Not all data on the LTA is public and you may have to
request access from the `Solar and Space Weather KSP <https://www.astron.nl/spaceweather/SolarKSP/>`__.

Request the data then download the data with **wget**.

Preprocess
----------
Raw LOFAR data must undergo a series a preprocessing steps before
it can be used for imaging.
Namely, these are auto-weighting and calibration.

autoweight
==========

Raw LOFAR data will have no 'WEIGHT' column in its measurement set (MS)
thus, it is necessary to do the autoweight step:

.. code:: bash

   DPPP msin=path/to/rawdata.MS msout=path/to/output.MS steps=[] msin.autoweight=true

This calculates the weights for the visibilities from the
auto-correlation data of the observation.

The script ``autoWeight.sh`` can batch this process if there is more than
one file.

(This step can be skipped if the measurement set is pre-processed by imaging pipeline.)

Calibration
============

Calibration of LOFAR data is performed using the `Default Preprocessing
Pipeline <https://dp3.readthedocs.io/en/latest/index.html>`__ (DPPP).

In order to use DPPP on the
`LOFAR computing facilities, <https://support.astron.nl/LOFARImagingCookbook/gettingstarted.html>`__
the following lines must be run:

.. code:: bash

    module load lofar
    module load dp3

The measurement set is calibrated with DPPP in three steps:

-  **Predict Calibration** : use the calibrator observation to predict the gain
   calibration solution.
-  **Apply Calibration** : apply the gain calibration solution to the solar observation.
-  **Apply Beam** : apply the LOFAR beam to the dataset.

These steps are covered in greater detail in the
`LOFAR Imaging Cookbook <https://support.astron.nl/LOFARImagingCookbook/dpppcalibrate.html>`__.
Below we give a short example of how to calibrate a raw LOFAR observation.

Predict Calibration
~~~~~~~~~~~~~~~~~~~

1.  Create a source.db file with a sky model of the calibrator. Here we use TauA as an example but other skymodels are available from `<https://github.com/lofar-astron/prefactor/tree/master/skymodels>`_.

.. code:: bash

   makesourcedb in=/path/to/TauA.skymodel out=TauA.sourcedb

2.  Run auto-weight with DPPP (Note: this step should be done for both sun and the calibrator):

.. code:: bash

   DPPP msin=/path/to/calibrator.MS
   msout=/path/to/calibrator-autow.MS
   steps=[]

   msin.autoweight=True

3.  Use the observation of the calibrator to predict the parameters for the calculation applied to the solar observation.

.. code:: bash

   DPPP msin=/path2/to/calibrator-autow.ms \
   Msout=. \
   steps=[gaincal] \
   gaincal.usebeammodel=True  \
   gaincal.solint=4 \
   gaincal.sources=TauA \
   gaincal.sourcedb=TauA.sourcedb \
   gaincal.onebeamperpatch=True \
   gaincal.caltype=diagonal

Apply Calibration
~~~~~~~~~~~~~~~~~

4.  Apply the parameters predicted by step (3)

.. code:: bash

   DPPP msin=/path2/to/sun-autow.ms \
   msout=. \
   msin.datacolumn=DATA \
   msout.datacolumn=CORR_NO_BEAM \
   steps=[applycal] \
   applycal.parmdb=/path/to/calibrator-autow.MS/instrument \
   applycal.updateweights=True

Apply Beam
~~~~~~~~~~

5.  Apply the beam model of the calculation for the LOFAR station:

.. code:: bash

   DPPP msin=sun-autow.MS \
   msout=. \
   msin.datacolumn=CORR_NO_BEAM \
   msout.datacolumn=CORRECTED_DATA \
   steps =[applybeam] \
   applybeam.updateweights=True

The steps (2)-(5) are integrated in the script ``auto_sun_calib.py`` to
calibrate the MS files in batch.


The script
`auto_sun_calib.py <https://github.com/peijin94/LOFAR-Sun-tools/blob/master/utils/IM/auto_sun_calib.py>`__
automizes the calibration of LOFAR observations. It generates the parset
file for the calibration and runs the corresponding DPPP commad.

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

Inspecting Calibration Solutions
--------------------------------

In many cases, solar radio bursts can contaminate the observation
of the calibrator source. It is thus **highly recommended** [#]_ that the
gain calibration solutions obtained with DPPP are visually inspected.
The `LOFAR Solution Tool <https://support.astron.nl/LOFARImagingCookbook/losoto.html>`__
(LoSoTo) can be used to plot the calibration solutions for each antenna 
pair using the ``cal_solution_plot.parset`` file below 

.. code:: bash

   [plot_amp]
   operation = PLOT
   axesInPlot = [time,freq]
   axisInTable = ant
   axisInCol = pol
   soltab = sol000/amplitude000
   markerSize = 4
   plotFlag = True
   makeAntPlot=False
   doUnwrap = False
   prefix=/path/to/calibration/solution/plots/output_name_amp_
   [plot_phase]
   operation = PLOT
   axesInPlot = [time,freq]
   axisInTable = ant
   axisInCol = pol
   soltab = sol000/phase000
   markerSize = 4
   plotFlag = True
   makeAntPlot=False
   doUnwrap = True
   prefix=/path/to/calibration/solution/plots/output_name_phase_

Use ``parmdb2H5parm.py`` to convert the calibration solutions stored at
``/path/to/calibrator-autow.MS/instrument`` to a H5 file compatible with 
LoSoTo and generate the calibration soultion plots as follows:

.. code:: bash

   parmdb2H5parm.py -v cal_solutions.h5  /path/to/calibrator-autow.MS/instrument
   losoto -v cal_solutions.h5 cal_solution_plot.parset

Clean
-----

Once the data has been calibrated, it can be imaged. We recommend using
`WSClean <https://wsclean.readthedocs.io/en/latest/index.html>`__ for this.
An example of WSClean for the sun:


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

A small cheatsheet for solar WSClean:

+--------+--------+----------------------------------------------------+
| C      | Par    | Comment                                            |
| ommand | ameter |                                                    |
+========+========+====================================================+
| -j     | 20     | Number of thread used for CLEAN (can be equal to   |
|        |        | the number of cores).                              |
+--------+--------+----------------------------------------------------+
| -mem   | 80     | Maximum memory limit in percent to the system      |
|        |        | memory. (Don't use 100%)                           |
+--------+--------+----------------------------------------------------+
| -weight| briggs | Weight for the baselines. Briggs 0 works for most  |
|        | 0.2    | of the situations                                  |
+--------+--------+----------------------------------------------------+
| -size  | 2048   | Size of the image in pixel.                        |
|        | 2048   |                                                    |
+--------+--------+----------------------------------------------------+
| -scale | 3asec  | The scale of one pixel, can be 0.1asec,3asec,      |
|        |        | 3min, 3deg. This should be less 1/4 the beam size  |
|        |        | in order to properly sample the beam.              |
+--------+--------+----------------------------------------------------+
| -pol   | I      | The polarization for cleaning, can be I,Q,U,V.     |
+--------+--------+----------------------------------------------------+
| -mult  | \\     | Whether to use multiscale in the clean. Better to  |
| iscale |        | switch on for extended source.                     |
+--------+--------+----------------------------------------------------+
| -data- | CO     | Be sure to use the calibrated data                 |
| column | RRECTE | (CORRECTED_DATA).                                  |
|        | D_DATA |                                                    |
+--------+--------+----------------------------------------------------+
| -niter | 2000   | The iteration of clean, for the sun, 400 is        |
|        |        | necessary, 1000 can be better, 2000 is enough.     |
+--------+--------+----------------------------------------------------+
| -i     | 85     | How many images you want to produce.               |
| nterva |        |                                                    |
| ls-out |        |                                                    |
+--------+--------+----------------------------------------------------+
| -in    | 3000   | The index range for the CLEAN.                     |
| terval | 4000   |                                                    |
+--------+--------+----------------------------------------------------+

For the interval index, one can use the ``get_datetime_index.py`` to find
out the starting and ending index.


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

For the use of jupyterlab, port forwarding can be done with:

.. code:: bash

   ssh -L 1234:localhost:1234  username@server_address

   source /data/scratch/zhang/conda_start.sh

   python -m jupyter notebook --no-browser --port=1234

Change username and 1234 accordingly.



Docker
-------------

Above steps requires LOFAR software, which is not easy to install. 
We can use docker to run steps.

For calibration we use the docker image from `here <https://hub.docker.com/r/lofarsoft/lofar>`__.

.. code:: bash

   $ docker run --rm -it lofaruser/imaging-pipeline:latest

   (in docker) $ source /opt/lofarsoft/lofarinit.sh

   (in docker) $ DPPP --version


For Visualization we use the docker image "peijin/lofarsun"

.. code:: bash

   $ docker run --rm --hostname lofarsoft -p 8899:8899 \
       -v /HDD/path/to/data/:/lofardata peijin/lofarsun \
       /bin/bash -c "jupyter-lab --notebook-dir=/lofardata \
       --ip='*' --port=8899 --no-browser --allow-root"

This command will start a jupyter lab server in the docker container, also mount the 
directory '/HDD/path/to/data/' to '/lofardata'



.. autofunction:: lofarSun.IM.get_peak_beam_from_psf





========================
LincSun
========================

The imaging data processing pipeline based on `LINC <https://linc.readthedocs.io/>`__ .

Requirements
------------

- `Singulartiy <https://sylabs.io/singularity/>`__
- `CWL <https://www.commonwl.org/>`__
- `LINC <https://linc.readthedocs.io/>`__

The tool is packaged as a singularity container, no need to install and configure the dependencies and software.

To pull the container:

.. code:: bash

   singularity pull docker://peijin94/lincsun:latest

To run the container as a shell:

.. code:: bash

   singularity -B /my/data:/my/data shell lincsun_latest.sif


Calibration with lincsun
------------------------

Prepare data and lincSun
~~~~~~~~~~~~~~~~~~~~~~~~

Data can be downloaded from LTA `here <https://lta.lofar.eu/Lofar>`__.

Assuming the data is stored in the directory '/path/to/data', with all MS files in the subdirectory 'MS'.

The data processing directory is '/path/to/proc'.

Download the source code:

.. code:: bash

   cd /path/to/proc
   git clone https://github.com/peijin94/LOFAR-Sun-tools.git
   cp -r ./LOFAR-Sun-tools/utils/IM/LINC ./


Prepare the json
~~~~~~~~~~~~~~~~

The workflows and steps of the data procedure is described in CWL files, can be found in the directory 'LINC/lincSun'

We need to prepare a json file to describe the data and the parameters for the data processing.

For example:

.. code::
   {
      "msin": [
         {
               "class": "Directory",
               "path": "/path/to/data/MS/Data001.MS"
         },
         {
               "class": "Directory",
               "path": "/path/to/data/MS/Data001.MS"
         }
      ],
      "ATeam_skymodel": {
         "class": "File",
         "path": "/path/to/somewhere/else/A-Team_lowres.skymodel"
      },
      "refant": "CS002LBA"
   }

This example json file tells the workflow to process Data001.MS and Data002.MS, with the A-Team skymodel and the reference antenna CS002LBA.

Then we can run the workflow with cwltool command inside the container "LINC":

.. code:: bash
   singularity exec -B /path/to/data/ -B $PWD \
       /path/to/contianer/linc_latest.sif \
      cwltool --outdir /path/to/proc/proc/ /path/to/proc/LincSun/workflow/calibrator_sun.cwl \
      /path/to/proc/calib.json

There are two steps in the workflow: **gaincal** and **applycal**, both are done with above way.


.. rubric:: Footnotes

.. [#] LoSoTo: LOFAR solutions tool

