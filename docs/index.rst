LOFAR Sun Tools
===============

Handy scripts and modules for the LOFAR data processing for Solar and
Space Weather. Installation guide `docs/install.md <doc/install.md>`__
For docker user:
`lofarsundocker <https://github.com/Pjer-zhang/lofarsunDocker>`__

Data Type
---------

-  (.MS) Interferometry raw data, measurement set.
   `docs/interferometry.md <doc/interferometry.md>`__
-  (.h5) Beamformed data, HDF5 format.
   `docs/beamformed.md <doc/beamformed.md>`__
-  (xxx-cube.fits) Beamformed data, fits
   cube.\ `docs/beamformed.md <doc/beamformed.md>`__
-  (xxx-image.fits) Interferometry image
   data.\ `docs/interferometry.md <doc/interferometry.md>`__

Install
-------

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

.. figure:: ./docs/img/image.png
   :alt: image

   image

Cite as
-------

https://arxiv.org/abs/2205.00065
