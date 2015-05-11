#! /bin/bash

# test analysis
GPS_START_TIME=1102660000
GPS_END_TIME=1102662000
IFO=L
FRAME_TYPE=L1_R

# run the datafind script to create a frame cache that contains
# the path of the frame files we requested
ligo_data_find --lal-cache --observatory ${IFO} --type ${FRAME_TYPE} --gps-start-time $GPS_START_TIME --gps-end-time $GPS_END_TIME --url-type file > frame_caches/L1-DATAFIND-${GPS_START_TIME}-$((${GPS_END_TIME}-${GPS_START_TIME})).lcf
