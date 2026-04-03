"""
WSGI config for django_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""
from pathlib import Path
import os
import sys
BASE_DIR = Path(__file__).resolve().parent.parent

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
venv = os.environ.get('GROW_VENV', None)
if venv:
    venv_path = Path(venv).resolve() / 'lib' / f"python{sys.version_info.major}.{sys.version_info.minor}" / 'site-packages'
    if venv_path.is_dir() and not str(venv_path) in sys.path:
        sys.path.insert(0, str(venv_path))

if not str(BASE_DIR) in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

from django.contrib.auth.handlers.modwsgi import (  # noqa: F401
    check_password,
    groups_for_user
)
