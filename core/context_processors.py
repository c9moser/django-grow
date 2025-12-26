from django.http import HttpRequest
from . import settings


def core(request: HttpRequest):
    return {
        'allow_signup': settings.ALLOW_SIGNUP,
        'include_wiki': settings.INCLUDE_WIKI,
    }
