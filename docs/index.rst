.. LOFAR-Sun documentation master file, created by
   sphinx-quickstart on Sun Jul  3 18:12:56 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to LOFAR-Sun's documentation!
=====================================

LOFAR data processing for Solar and Space Weather. 


The LOw Frequency ARray (LOFAR) is a large-scale array of radio telescopes, it can perform multiple flexible type of observations, 
making it a great instrument for solar and space weather studys:

:Solar imaging:
   - **Interferometry imaging**, high spatial resolution (~ arcmin), low time resolution (>0.1s), low frequency resolution (~0.5 MHz).
   - **Tied array beam imaging**, high time resolution (1/96s), high frequency resolution (0.02 MHz), low spatial resolution (~ 0.4 Deg).

:Solar spectroscopy:
   - **Beamformed dynamic spectrum**, no spatial resolution,  high time resolution (1/96s), high frequency resolution (0.02 MHz).

:Heliosphere:
   - **Beamformed dynamic spectrum** of quasars, for interplanetary scintillation.
   - **Pulsar observations** for solar wind plasma and CMEs.


.. figure:: img/logo.png
   :alt: LOFAR logo
   :width: 300px
   :align: center





For docker user:
`lofarsundocker <https://github.com/Pjer-zhang/lofarsunDocker>`__



.. toctree::
   :maxdepth: 2
   :caption: Quick start
   :hidden:

   /install



Solar imaging
-----------------


-  (.MS) Interferometry raw data, measurement set.
   `interferometry <interferometry.html>`__
-  (xxx-cube.fits) Beamformed data, fits
   cube.\ `beamformed <beamformed.html>`__
-  (xxx-image.fits) Interferometry image
   data.\ `interferometry <interferometry.html>`__



.. toctree::
   :maxdepth: 2
   :caption: Interferometry
   :hidden:

   /interferometry



Beamformed data
-----------------


-  (.h5) Beamformed data, HDF5 format.
   `beamformed <beamformed.html>`__

.. toctree::
   :maxdepth: 2
   :caption: Beamformed
   :hidden:

   /beamformed



Go to a empty directory, run the following command.

.. code:: bash

   git clone https://github.com/peijin94/LOFAR-Sun-tools.git
   cd LOFAR-Sun-tools
   # (conda activate xxx)
   python setup.py install

Run quick view for TAB-cube-fits:

.. code:: bash

   # (conda activate xxx)
   lofarBFcube

Then load beamformed imaging fits and preview:

.. figure:: img/bfcube.png
   :alt: image

   image

Cite as
-------

https://arxiv.org/abs/2205.00065




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
