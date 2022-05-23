# LOFAR Sun Tools

 Handy scripts and modules for the LOFAR data processing for Solar and Space Weather.
 Installation guide [doc/install.md](doc/install.md)
 For docker user: [lofarsundocker](https://github.com/Pjer-zhang/lofarsunDocker)

## Data Type

* (.MS) Interferometry raw data, measurement set. [doc/interferometry.md](doc/interferometry.md)
* (.h5) Beamformed data, HDF5 format. [doc/beamformed.md](doc/beamformed.md)
* (xxx-cube.fits) Beamformed data, fits cube.[doc/beamformed.md](doc/beamformed.md)
* (xxx-image.fits) Interferometry image data.[doc/interferometry.md](doc/interferometry.md)

## Install

```bash
git clone https://github.com/peijin94/LOFAR-Sun-tools.git
cd LOFAR-Sun-tools
# (conda activate xxx)
python setup.py install
```

Run quick view for TAB-cube-fits:
```bash
# (conda activate xxx)
lofarBFcube
```
Then load beamformed imaging fits and preview:

![image](./doc/img/image.png)
