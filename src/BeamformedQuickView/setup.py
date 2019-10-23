#from distutils.core import setup
from setuptools import setup
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
  name = 'lofarSun',         # How you named your package folder (MyLib)
  packages = ['lofarSun'],   # Chose the same as "name"
  version = '0.1.5',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'tools to process the lofar solar data',   # Give a short description about your library
  author = 'Peijin',                   # Type in your name
  author_email = 'pjer1316@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/Pjer-zhang/LOFAR_Solar',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/Pjer-zhang/LOFAR_Solar/archive/master.zip',    # I explain this later on
  keywords = ['LOFAR', 'Solar', 'radio'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'matplotlib',
          'sunpy',
          'opencv-python',
          'astropy',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
  long_description=long_description,
  long_description_content_type='text/markdown'
)