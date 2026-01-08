#!/bin/sh
self=$(realpath "$0")
basedir=$(dirname "$self")

export DJANGO_SETTINGS_MODULE="grow.settings"
export PYTHONPATH="$basedir/grow:$PYTHONPATH"

if [ -z "$1" -o "$1" = "runserver" -o "$1" = "run" ]; then
    shift
    python3 "$basedir/manage.py" runserver "$@"
    exit 0
elif [ "$1" = "shell" ]; then
    python3 "$basedir/manage.py" shell
    exit 0
elif [ "$1" = "migrate" ]; then
    python3 "$basedir/manage.py" migrate
    exit 0
elif [ "$1" = "makemigrations" ]; then
    python3 "$basedir/manage.py" makemigrations
    exit 0
elif [ "$1" = "collectstatic" ]; then
    python3 "$basedir/manage.py" collectstatic --noinput
    exit 0
elif [ "$1" = "createsuperuser" ]; then
    python3 "$basedir/manage.py" createsuperuser
    exit 0
elif [ "$1" = "test" ]; then
    shift
    python3 "$basedir/manage.py" test "$@"
    exit 0
elif [ "$1" = "growimport" ]; then
    shift
    python3 "$basedir/manage.py" growimport "$@"
    exit 0
elif [ "$1" = "growexport" ]; then
    shift
    python3 "$basedir/manage.py" growexport "$@"
    exit 0
elif [ "$1" = "makemessages" ]; then
    shift
    python3 "$basedir/manage.py" makemessages "$@"
    exit 0
elif [ "$1" = "compilemessages" ]; then
    shift
    python3 "$basedir/manage.py" compilemessages "$@"
    exit 0
elif [ "$1" = "compilemessages" ]; then
    shift
    python3 "$basedir/manage.py" compilemessages "$@"
    exit 0
elif [ "$1" = "help"]; then
    echo "Usage: ${0##*/} [command] [options]"
    echo "Commands:"
    echo "  runserver [addrport]       Run the development server"
    echo "  shell                      Open a Django shell"
    echo "  migrate                    Apply database migrations"
    echo "  makemigrations             Create new database migrations"
    echo "  collectstatic              Collect static files"
    echo "  createsuperuser            Create a superuser account"
    echo "  test [app_label]           Run tests for the specified app"
    echo "  growimport [options]       Import data into the application"
    echo "  growexport [options]       Export data from the application"
    echo "  makemessages [options]     Create message files for translation"
    echo "  compilemessages [options]  Compile message files for translation"
    exit 0
elif [ "$1" = "uwsgi" ]; then
    shift
    if [ -f "$basedir/uwsgi.ini" ]; then
        exec uwsgi --ini "$basedir/uwsgi.ini" "$@"
    else
        exec uwsgi --module grow.wsgi:application --master --http :8000 --processes 4 --threads 2 "$@"
    fi
elif [ "$1" = "${1#-}" ]; then
    exec python3 "$basedir/manage.py" "$@"
else
    exec "$@"
fi
