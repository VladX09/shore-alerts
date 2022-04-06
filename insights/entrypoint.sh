#!/bin/bash
set -e

case "$1" in
    test)
        pytest --log-level=DEBUG 
        ;;
    start)
        python insights_app/jobs/price_decrease_job.py "${@:2}"
        ;;
    *)
        exec "$@"
        ;;
esac
