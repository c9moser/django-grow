from typing import Any
from django.http import HttpRequest
from . import settings


def grow(request: HttpRequest) -> dict[str, Any]:
    """
    grow contexts
    """

    return {
        'base_template': settings.BASE_TEMPLATE,
        'use_bootstrap': settings.USE_BOOTSTRAP,
        'grow_site_title': settings.GROW_SITE_TITLE,
        'site_title': settings.GROW_SITE_TITLE,
        'grow_head_title': settings.GROW_HEAD_TITLE,
    }
