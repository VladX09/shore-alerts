#!/bin/bash
set -e

case "$1" in
    test)
        pytest --log-level=DEBUG 
        ;;
    start)
        PARAMS=${2:}
        python insights_app/jobs/price_decrease_job.py $PARAMS
        ;;
    *)
        exec "$@"
        ;;
esac
