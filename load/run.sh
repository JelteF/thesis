#!/bin/bash

log_dir=/var/log/nginx/


echo "cd $log_dir;" rm cache.log | cat - purge_cache.sh \
    | ssh root@cache 'bash -s'

tests='nocache.cdn cdn ismproxy nocache.transmux single.transmux double.transmux'

for i in `seq 2`; do
    for prefix in $tests; do
        export URL_PREFIX=$prefix
        # make clean
        for con in 1 2 5 10 25 50; do
            export CONNECTIONS=$con
            make fmp4-dash-log
            make fmp4-hds-log
            make fmp4-hls-log
            make fmp4-iss-log
            echo "cd $log_dir;" mv cache.log "$URL_PREFIX".log | cat - purge_cache.sh \
                | ssh root@cache 'bash -s'
        done
    done
done
