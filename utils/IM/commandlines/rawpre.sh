mkdir MS_aw
baseDIR='./MS'
MSfnames=`ls $baseDIR`
for MSfile in $MSfnames; do
        NDPPP msin=$baseDIR/$MSfile steps=[averager] \
        averager.timestep=60 averager.freqstep=16 msout=MS_aw/$MSfile msin.autoweight=True  #(only for raw)
done

