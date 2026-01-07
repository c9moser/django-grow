from django.http import HttpRequest
from . import settings
# from django.conf import settings

from django.utils.translation import get_language


def core(request: HttpRequest):
    age_gate_needs_confirmation = (settings.AGE_GATE_REQUIRED
                                   and settings.AGE_GATE_NAME not in request.COOKIES)

    age_gate_confirmed = request.COOKIES.get(settings.AGE_GATE_NAME, 'false') == 'true'
    return {
        'allow_signup': settings.ALLOW_SIGNUP,
        'include_wiki': settings.INCLUDE_WIKI,
        'html_language': get_language().split('-', 1)[0],
        'cookies_consent_required': settings.COOKIES_CONSENT_REQUIRED,
        'cookies_consent_name': settings.COOKIES_CONSENT_NAME,
        'age_gate_needs_confirmation': age_gate_needs_confirmation,
        'age_gate_confirmed': age_gate_confirmed,
        'age_gate_required': settings.AGE_GATE_REQUIRED,
        'age_gate_name': settings.AGE_GATE_NAME,
        'age_gate_minimum_age': settings.AGE_GATE_MINIMUM_AGE,
        'age_gate_rejected_url': settings.AGE_GATE_REJECTED_URL,
    }
