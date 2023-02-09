#from distutils.core import setup
import setuptools
from setuptools import setup
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory,'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
  name = 'lofarSun',         # How you named your package folder 
  packages = setuptools.find_packages(),#['lofarSun','lofarSun.IM','lofarSun.BF','lofarSun.BF.GUI'],   # Chose the same as "name"
  include_package_data=True,
  version = '0.3.28',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'tools to process the lofar solar data',   # Give a short description about your library
  author = 'Peijin',                   # Type in your name
  author_email = 'pjer1316@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/peijin94/LOFAR-Sun-tools',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/peijin94/LOFAR-Sun-tools/archive/refs/heads/master.zip',    
  keywords = ['LOFAR', 'Solar', 'radio'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'matplotlib',
          'sunpy',
          'astropy',
          'h5py','pyqt5','pandas',
          'scipy',
          'numpy',
          'scikit-image'
      ],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',     # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license,
    'Programming Language :: Python :: 3.8',
  ],
  entry_points={'console_scripts': ['lofarBFcube=lofarSun.BF.GUI.lofarBFgui:main',
                                    'h5toFitsDS=lofarSun.cli.h5_to_fits_spec:main',
                                    'pymsOverview=lofarSun.cli.pyms_utils:pyms_overview_main',
                                    'pymsCookWscleanCMD=lofarSun.cli.pyms_utils:pyms_cook_wsclean_cmd_main',
                                    'pymsDatetime2Index=lofarSun.cli.pyms_utils:pyms_datetime_to_index_main',
                                    'pymsIndex2Datetime=lofarSun.cli.pyms_utils:pyms_index_to_datetime_main']},
  long_description=long_description,
  long_description_content_type='text/markdown'
)
