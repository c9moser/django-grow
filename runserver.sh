#!/bin/sh
self="$(realpath "$0")"
basedir="$(dirname "$self")"

export DJANGO_SETTINGS_MODULE="django_project.settings"
export PYTHONPATH="$basedir/grow:$PYTHONPATH"



if [ -z "$1" ]; then
    echo "No command provided. Use 'help' for usage information."
	exit 0
fi
case "$1" in
   runserver|run)
        shift
        exec poetry run python manage.py runserver "$@"
        exit $?
    ;;
    shell)
        shift
        exec poetry run python manage.py shell
        exit $?
    ;;
    migrate)
        shift
        exec poetry run python manage.py migrate "$@"
        exit $?
    ;;
    makemigrations)
        shift
        exec poetry run python manage.py makemigrations "$@"
        exit $?
    ;;
    collectstatic)
        shift
        exec poetry run python manage.py collectstatic --noinput "$@"
        exit $?
    ;;
    createsuperuser)
        shift
        exec poetry run python manage.py createsuperuser "$@"
        exit $?
    ;;
    test)
        shift
        exec poetry run python manage.py test "$@"
        exit $?
    ;;
    growimport)
        shift
        exec poetry run python manage.py growimport "$@"
        exit $?
    ;;
    growexport)
        shift
        exec poetry run python manage.py growexport "$@"
        exit $?
    ;;
    makemessages)
        shift
        exec poetry run python manage.py makemessages "$@"
        exit $?
    ;;
    compilemessages)
        shift
        exec poetry run python manage.py compilemessages "$@"
        exit $?
    ;;
    help)
        echo "Usage: ${0##*/} [command] [options]"
        echo "Commands:"
        echo "  runserver [addrport]       Run the development server"
        echo "  shell                      Open a Django shell"
        echo "  migrate                    Apply database migrations"
        echo "  makemigrations             Create new database migrations"
        echo "  collectstatic              Collect static files"
        echo "  createsuperuser [options]  Create a superuser account"
        echo "  test [app_label]           Run tests for the specified app"
        echo "  growimport [options]       Import data into the application"
        echo "  growexport [options]       Export data from the application"
        echo "  makemessages [options]     Create message files for translation"
        echo "  compilemessages [options]  Compile message files for translation"
        exit 0
    ;;
    uwsgi)
        shift
            if [ -f "$basedir/django_project/local/uwsgi.ini" ]; then
	            exec uwsgi --init "$basedir/django_project/local/uwsgi.ini" "$@"
            elif [ -f "$basedir/uwsgi.ini" ]; then
                exec uwsgi --ini "$basedir/uwsgi.ini" "$@"
            else
                exec uwsgi --module grow.wsgi:application --master --http :8000 --processes 4 --threads 2 "$@"
            fi
            exit $?
        ;;
    *)
        echo "Unknown command: $1. Use 'help' for usage information."
        exec "$@"
        exit $?
    ;;
esac
