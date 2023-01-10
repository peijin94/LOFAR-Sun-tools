#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=20
#SBATCH -J LOFAR-calib
#SBATCH --mem=64G
#SBATCH --constraint=avx
#SBATCH --array=0-243
#SBATCH --clusters=kale
#SBATCH --partition=short
#SBATCH --time=03:59:00
#SBATCH --mail-user=peijin.zhang@helsinki.fi

#------------------------------------------------------
# This script is used to clip a time range of data
# from the raw data
# (specifically for a small event in a huge MS dataset)
#------------------------------------------------------

# Note : make sure there is enough storage!

# /wrk -> /wrk-kappa
DIR='/wrk/group/corona/radio/LC4_001/'
DIR_OUT='/wrk/group/corona/peijin/LC4/MStgt/t1245_1305/'
SASID='L401013'
STARTTIME='2015/10/16/12:45:00'
ENDTIME='2015/10/16/13:05:00'

FILEDIRS=(${DIR}${SASID}*.MS)
MSDIR=${FILEDIRS[$SLURM_ARRAY_TASK_ID]}
MSNAME=`basename ${MSDIR}`
# show the 2nd file name
echo "processing:"${MSNAME}

# autoweight necessary for raw
# flagging better be done for calibrator
# msin.autoweight=True \


srun singularity exec -B /proj/group/corona/radio/,/wrk/group/corona/ \
    /proj/group/corona/radio/lofar-pipeline.simg \
    bash -c "source /opt/lofarsoft/lofarinit.sh && sleep 1 && time \
    NDPPP msin=$MSDIR steps=[]  \
    msin.starttime=$STARTTIME msin.endtime=$ENDTIME \
    msout=$DIR_OUT`basename $MSDIR` && \
    echo 'done' && sleep 1"

#flag.memoryperc=50