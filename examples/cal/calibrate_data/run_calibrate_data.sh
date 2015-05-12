#! /bin/bash

# test analysis
GPS_START_TIME=1102660000
GPS_END_TIME=1102660200
IFO=L
FRAME_TYPE=L1_R
FRAME_CACHE=frame_caches/L1-DATAFIND-${GPS_START_TIME}-$((${GPS_END_TIME}-${GPS_START_TIME})).lcf

# run the datafind script to create a frame cache that contains
# the path of the frame files we requested
ligo_data_find --lal-cache --observatory ${IFO} --type ${FRAME_TYPE} --gps-start-time $GPS_START_TIME --gps-end-time $GPS_END_TIME --url-type file > ${FRAME_CACHE}

# calibrate data
python pycbc_calibrate_data --gps-start-time ${GPS_START_TIME} --gps-end-time ${GPS_END_TIME} --frame-cache ${FRAME_CACHE}
