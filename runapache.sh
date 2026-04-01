#!/bin/bash

runserver() {
    #apachectl configtest || { echo "Apache configuration test failed. Aborting."; exit 1; }
    . /etc/apache2/envvars
    sudo -u www-data ./manage migrate --noinput || { echo "Database migration failed. Aborting."; exit 1; }
    apache2 -t || { echo "Apache configuration test failed. Aborting."; exit 1; }
    exec apache2 -D FOREGROUND -E /var/log/apache2/startup-errors.log -k start
    rc=$?
    echo "Apache exited with code $rc"
    if [ $rc -ne 0 ]; then
        [ -f /var/log/apache2/startup-errors.log ] && cat /var/log/apache2/startup-errors.log
        exit $rc
    fi
}

stopserver() {
    . /etc/apache2/envvars
    apache2 -k stop
    return $?
}

SELF="$(realpath "$0")"
BASE_DIR="$(dirname "$0")"
cd "$BASE_DIR"

if [ -z "$1" ]; then
    echo "No command provided. Defaulting to 'runserver'."
    runserver
    exit 0
fi

case "$1" in
    runserver|run|start)
        shift
        runserver
        exit $?
    ;;
    stop|stopserver)
        stopserver
        exit $?
    ;;
    manage)
        shift
        sudo -u www-data ./manage "$@"
        exit $?
    ;;
    migrate)
        shift
        sudo -u www-data ./manage migrate "$@"
        exit $?
    ;;
    collectstatic)
        shift
        sudo -u www-data ./manage collectstatic --noinput "$@"
        exit $?
    ;;
    shell)
        shift
        sudo -u www-data ./manage shell "$@"

        exit $?
    ;;
    sh)
        shift
        bash "$@"
        exit $?
    ;;
    update)
        shift
        sudo -u www-data ./manage migrate --noinput && \
        sudo -u www-data ./manage collectstatic --noinput && \
        stopserver && \
        runserver
        exit $?
    ;;
    help)
        echo "Usage: ${0##*/} [command] [options]"
        echo "Commands:"
        echo "  runserver, run              Start the Apache server"
        echo "  manage [options]            Run a Django management command"
        echo "  migrate [options]           Apply database migrations"
        echo "  collectstatic [options]     Collect static files"
        echo "  shell [options]             Start a Django shell"
        echo "  sh [options]                Start a bash shell"
        echo "  help                        Show this help message"
        exit 0
    ;;
    *)
        echo "Unknown command: $1. Use 'help' for usage information."
        exit 1
    ;;
esac
