"""
core settings

The settings are only used for the django project.
"""
from django.conf import settings

#: Allow users to sign up
ALLOW_SIGNUP = getattr(settings, 'ALLOW_SIGNUP', True)
INCLUDE_WIKI = getattr(settings, 'INCLUDE_WIKI', False)
AGE_GATE_REQUIRED = getattr(settings, 'AGE_GATE_REQUIRED', False)
AGE_GATE_NAME = getattr(settings, 'AGE_GATE_NAME', 'age_gate_passed')
AGE_GATE_MINIMUM_AGE = getattr(settings, 'AGE_GATE_MINIMUM_AGE', 18)
AGE_GATE_REJECTED_URL = getattr(settings, 'AGE_GATE_REJECTED_URL', '/age-gate/')
COOKIES_CONSENT_REQUIRED = getattr(settings, 'COOKIES_CONSENT_REQUIRED', False)
COOKIES_CONSENT_NAME = getattr(settings, 'COOKIES_CONSENT_NAME', 'cookies_consent')
