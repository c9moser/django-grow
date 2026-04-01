import logging


class DjangoAutoReloadFilter(logging.Filter):
    """
    Filter to exclude log messages related to Django's auto-reloader.
    """

    def filter(self, record):
        if record.name == 'django.utils.autoreload':
            return False
        return True
