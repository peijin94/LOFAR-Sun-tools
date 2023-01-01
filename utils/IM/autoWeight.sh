# By Peijin 
# 2020-9-17

# Note : make sure there is enough storage!

DIR='/data001/scratch/zucca/EVENT_20220521/MS/'

module load dp3 lofar # load NDPPP 

PREFIX='L'

# needs to do autoweight for raw

# flagging better be done for calibrator
for MSfile in `ls $DIR$PREFIX*SAP001*.MS -d`
do             
  NDPPP msin=$MSfile msin.autoweight=True \
  steps=[flag,averager] averager.freqstep=16 \
  flag.type=aoflagger flag.memoryperc=85 \
  flag.timewindow=64 msout=./MS_aw/`basename $MSfile`  
done

# flagging needs to be done for quiet Sun
# flagging should not be done for burst time
for MSfile in `ls $DIR$PREFIX*SAP000*.MS -d`
do
  NDPPP msin=$MSfile steps=[averager] \
  msin.autoweight=True averager.freqstep=16 \
  msout=./MS_aw/`basename $MSfile`  
done