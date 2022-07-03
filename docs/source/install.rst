Step by step intall guide
=========================

Install lofar-sun-tool from scratch.

Install conda
-------------

(see anaconda.org)

Create virtual enviroment
-------------------------

We recommend creating a standalone python enviroment for a more isolated
and stable runtime.

.. code:: bash

   conda create -n lofarsun python=3.8

Then activate the enviroment:

.. code:: bash

   conda activate lofarsun

Install dependencies
--------------------

.. code:: bash

   conda install -c conda-forge sunpy==2.0.6 matplotlib jupyterlab opencv scikit scikit-image hdf5 opencv

note : pip higher priority than conda

Install lofarSun
----------------

From pip

.. code:: bash

   python -m pip install lofarSun

From git

.. code:: bash

   git clone https://git.astron.nl/ssw-ksp/lofar-sun-tools.git
   cd lofar-sun-tools/pro/src
   python setup.py install

:sub:`Enjoy`
