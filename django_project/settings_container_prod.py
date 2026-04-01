from logging import DEBUG


STATIC_ROOT = '/var/www/grow/static'
MEDIA_ROOT = '/var/www/grow/media'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/data/db.sqlite3',
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'django_browser_reload': {
            'class': 'grow.growapi.logging.DjangoAutoReloadFilter'
        }
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/apache2/grow.debug.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
