.. LOFAR-Sun documentation master file, created by
   sphinx-quickstart on Sun Jul  3 18:12:56 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to LOFAR-Sun's documentation!
=====================================



Handy scripts and modules for the LOFAR data processing for Solar and
Space Weather. 

For docker user:
`lofarsundocker <https://github.com/Pjer-zhang/lofarsunDocker>`__

Data Type
---------

-  (.MS) Interferometry raw data, measurement set.
   `interferometry.rst <interferometry.rst>`__
-  (.h5) Beamformed data, HDF5 format.
   `beamformed.rst <beamformed.rst>`__
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




.. toctree::
   :maxdepth: 2
   :caption: Quick start
   :hidden:
   /install
   

.. toctree::
   :maxdepth: 2
   :caption: Interferometry
   :hidden:
   /interferometry


.. toctree::
   :maxdepth: 2
   :caption: Beamformed
   :hidden:
   /beamformed






Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
