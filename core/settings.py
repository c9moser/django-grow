"""
core settings

The settings are only used for the django project.
"""
from django.conf import settings

#: Allow users to sign up
ALLOW_SIGNUP = getattr(settings, 'ALLOW_SIGNUP', True)
INCLUDE_WIKI = getattr(settings, 'INCLUDE_WIKI', False)
