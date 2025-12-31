from django.http import HttpRequest
from . import settings
# from django.conf import settings

from django.utils.translation import get_language


def core(request: HttpRequest):
    return {
        'allow_signup': settings.ALLOW_SIGNUP,
        'include_wiki': settings.INCLUDE_WIKI,
        'html_language': get_language().split('-', 1)[0],
    }
