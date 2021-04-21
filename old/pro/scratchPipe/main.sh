#!/bin/bash

# untar everything
python untar.py

# autoweight
module load dp3 lofar # load NDPPP 

DIR='./'  # better use absolute directory
PREFIX='L'

for MSfile in `ls $DIR$PREFIX*.MS -d`
do
    NDPPP msin=$MSfile msout=${MSfile/uv/autow_uv} steps=[] msin.autoweight=True && rm -r $MSfile
done

python autoCalib.py
