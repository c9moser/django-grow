from django.conf import settings
from grow.api.settings import *  # noqa

BASE_TEMPLATE = getattr(settings, "BASE_TEMPLATE", "grc/base.html")
USE_BOOTSTRAP = getattr(settings, "USE_BOOTSTRAP", False)
