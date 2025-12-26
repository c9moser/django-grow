from typing import Any
from django.http import HttpRequest
from . import settings

from django.conf import settings as django_settings


def grc_context(request: HttpRequest) -> dict[str, Any]:
    return {
        'base_template': settings.BASE_TEMPLATE,
        'allow_signup': getattr(django_settings, 'ALLOW_SIGNUP', True),
    }
