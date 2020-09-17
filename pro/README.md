# Steps of Solar Imaging 

## Download or Stage data (.MS file)

The LOFAR data is stored at [LTA](https://lta.lofar.eu/Lofar)

Request the data then download the data with **wget**

## Preprocess

If the data is un-calibrated data, do use the NDPPP to auto weight the data set:

```bash
NDPPP msin=path/to/rawdata.MS msout=path/to/output.MS steps=[] msin.autoweight=true
```

The script autoWeight.sh can batch this process if there is more than one file

(This step can be skipped if the measurement set has been calibrated.)

## Calibration

The meassurement set is calibrated with NDPPP in three steps:

- **Predicted Calculation** : use the calibrator to predict the gain calculation
- **Apply Calculation** : apply the gain calculation to the sun
- **Apply Beam** : apply the LOFAR beam to the dataset

These steps can be done with a script **auto\_sun\_calib.py**

## Plot

wsclean will produce the CLEANed radio image in the form of fits file. The flux intensity is in the form of Jy/Beam, Which can be converted to The brightness temperature with the Equation given in [Flux intensity](https://science.nrao.edu/facilities/vla/proposing/TBconv)

In python, this can be done with:
```python
beamArea = (b_maj/180*np.pi)*(b_min/180*np.pi)*np.pi /(4*np.log(2))
data_Tb = data_Jy_beam*(300/freq_cur)**2/2/(1.38e-23)/1e26/beamArea
```

Where the **freq_cur** is the current frequency in MHz, 1.38e-23 is the Boltzman constant, **beamArea** is the solid angle of fitted beam
