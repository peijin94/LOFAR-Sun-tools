
# download
wget -i html.txt

# untar and archieve
python2 untar.sh
mkdir MS
mv *.MS MS

# autoweight with averaging [for raw only]
source rawpre.sh 

# calibration
python batch_sun_calib.py #(auto_sun_calib.py)

# wsclean
wsclean.sh

