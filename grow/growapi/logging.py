import logging


class DjangoAutoRealodFilter(logging.Filter):
    """
    Filter to exclude log messages related to Django's auto-reloader.
    """

    def filter(self, record):
        # Exclude messages that contain "Watching for file changes with StatReloader"
        if record.name == 'django.utils.autoreload':
            return False
        return True
