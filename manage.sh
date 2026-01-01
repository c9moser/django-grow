#!/bin/sh
self="$(realpath $0)"
base_dir="$(dirname "$self")"

cd "$base_dir"
poetry run python manage.py "$@"

