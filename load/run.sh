#!/bin/bash

log_dir=/var/log/nginx/


echo "cd $log_dir;" rm cache.log | cat - purge_cache.sh \
    | ssh root@cache 'bash -s'

tests='nocache.basic'

for prefix in $tests; do
    export URL_PREFIX=$prefix
    make clean
    make link
    make fmp4-iss-log
    # make fmp4-dash-log
    # make fmp4-hls-log
    # make fmp4-hds-log
    echo "cd $log_dir;" mv cache.log "$URL_PREFIX".log | cat - purge_cache.sh \
        | ssh root@cache 'bash -s'
done
