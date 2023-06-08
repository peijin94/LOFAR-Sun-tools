# By Peijin 
# 2022-01-04

# Note : make sure there is enough storage!

DIR='/proj/group/corona/radio/peijin/data/L401011/'

PREFIX='L'
namecalib='401011'
namesun='401013'

# autoweight necessary for raw
# flagging better be done for calibrator
# msin.autoweight=True \
for MSfile in `ls $DIR$PREFIX*$namecalib*.MS -d`
do             
  NDPPP msin=$MSfile \
  steps=[flag,averager] averager.freqstep=16 averager.timestep=40 \
  flag.type=aoflagger flag.memoryperc=85 averager.strategy=LBAdefault\
  flag.timewindow=64 msout=./MS_aw/`basename $MSfile`  
done

# flagging needs to be done for quiet Sun
# flagging should not be done for burst time
# averaging is optional
for MSfile in `ls $DIR$PREFIX*$namesun*.MS -d`
do
  NDPPP msin=$MSfile \
  steps=[averager] averager.freqstep=16 \
  msout=./MS_aw/`basename $MSfile`  
done