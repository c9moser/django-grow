from django.conf import settings
from grow.api.settings import *  # noqa

BASE_TEMPLATE = getattr(settings, "BASE_TEMPLATE", "grow/base.html")
USE_BOOTSTRAP = getattr(settings, "USE_BOOTSTRAP", False)
LOGIN_REQUIRED = getattr(settings, "LOGIN_REQUIRED", False)
