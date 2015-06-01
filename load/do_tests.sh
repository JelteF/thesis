#!/bin/bash

log_dir=/var/log/apache2/
log_file=origin-size.log

url_file_dir=files
iss_file=$url_file_dir/fmp4-iss-log
hls_file=$url_file_dir/fmp4-hls-log
dash_file=$url_file_dir/fmp4-hds-log
hds_file=$url_file_dir/fmp4-hls-log

url_files="$iss_file $hls_file $dash_file $hds_file"

function connect_to_storage {
    ssh root@storage 'bash -s'
}

function connect_to_cache {
    ssh root@cache 'bash -s'
}

function calculate_storage_trafic {
    echo "cd $log_dir;" \
        "cat $log_file | tr ' ' '\\n' | paste -sd+ | bc" \
        | connect_to_storage
}

function get_nr_requests {
    echo "cd $log_dir;" \
        "cat $log_dir/$log_file | wc -l" \
        | connect_to_storage
}


function clear_storage_log {
    echo "cat /dev/null > $log_dir/$log_file" \
        | connect_to_storage
}

function get_cache_used {
    echo "du -s /var/cache/nginx | cut -f1" \
        | connect_to_cache
}

function get_results {
    clear_storage_log;
    echo -n test_time:
    date -u +"%Y-%m-%dT%T.%3N" >> $2;
    do_requests_with_write $1 $2 $3
    echo internal_bytes: `calculate_storage_trafic` >> $2
    echo internal_requests: `get_nr_requests` >> $2
    echo cache_usage: `get_cache_used` >> $2
}

function do_requests_with_write {
    print_request_command $1 $3
    do_requests $1 $3 | grep 'elapsed time\|{.*}' >> $2;
}

function do_requests_without_write {
    print_request_command $1 $2
    do_requests $1 $2 > /dev/null
}

function print_request_command {
    echo $WRK -t 1 -d $DURATION -s $SCRIPT -c $CONNECTIONS $URL -- $1 $2
}

function do_requests {
    $WRK -t 1 -d $DURATION -s $SCRIPT -c $CONNECTIONS $URL -- $1 $2
}

function purge_cache {
    cat purge_cache.sh | connect_to_cache
}

echo going to write stuff to $2


for run_type in first_time second_time after_other; do
    echo -e "\nrun_type:" $run_type >> $2;
    echo running $run_type;
    for i in `seq $RUNS`; do
        if [ "$run_type" == "second_time" ]; then
            echo hiero $i
            get_results $1 $2 multiple
        else
            echo no hiero $i
            if [ "$run_type" == "after_other" ]; then
                for first_run in $url_files; do
                    if [ "$first_run" != "$1" ]; then
                        echo after: $first_run >> $2
                        echo running after $first_run
                        purge_cache
                        do_requests_without_write $first_run once
                        get_results $1 $2 once
                    fi
                done
            else
                echo doing the first actually
                get_results $1 $2 once
            fi
        fi
    done
done
