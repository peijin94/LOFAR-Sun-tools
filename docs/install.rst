Install
=========================

LOFAR imaging software
-----------------------

The dependencies of imaging software is very complex, we recommend using docker or singularity to run the software.
`LOFAR imaging with docker <https://support.astron.nl/LOFARImagingCookbook/buildlofar.html>`__


LOFAR Sun 
-------------------------

For the dynamic spectrum and imaging postprocess, we use python package :code:`lofarSun` (`lofarSun   <https://github.com/peijin94/LOFAR-Sun-tools>``).
We recommend creating a standalone python enviroment for a more isolated
and stable runtime.

.. code:: bash

   conda create -n lofarsun python=3.9

Then activate the enviroment:

.. code:: bash

   conda activate lofarsun

From pip, the (relatively) stable version:

.. code:: bash

   python -m pip install lofarSun

From git the (nighty) dev version:

.. code:: bash

   git clone https://git.astron.nl/ssw-ksp/lofar-sun-tools.git
   cd lofar-sun-tools/pro/src
   python setup.py install


Also, we can use docker to run lofarSun: 
`lofarsundocker <https://github.com/Pjer-zhang/lofarsunDocker>`__

