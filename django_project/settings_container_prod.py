
import environ
from pathlib import Path

DEBUG = False
ALLOWED_HOSTS = ['*']

env = environ.Env(
    GROW_STATIC_ROOT=(str, '/var/www/grow/static'),
    GROW_MEDIA_ROOT=(str, '/var/www/grow/media'),
    GROW_DB=(str, 'sqlite3:////data/db.sqlite3'),
)
STATIC_ROOT = Path(env('GROW_STATIC_ROOT')).resolve()
MEDIA_ROOT = Path(env('GROW_MEDIA_ROOT')).resolve()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'django_browser_reload': {
            'class': 'grow.growapi.logging.DjangoAutoReloadFilter'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'filters': ['django_browser_reload'],
            'formatter': 'console',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/grow/grow.log',
            'filters': ['django_browser_reload'],
            'formatter': 'file',
        },
    },
    'formatters': {
        'verbose': {
            'format': '[{asctime}|{levelname}|{name}] {message}',
            'style': '{',
        },
        'file': {
            'format': '[{asctime}|{levelname}|{name}] {message}',
            'style': '{',
        },
        'console': {
            'format': '[{levelname}|{name}] {message}',
            'style': '{',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'grow': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
