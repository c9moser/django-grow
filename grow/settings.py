from django.conf import settings
from grow.api.settings import *  # noqa

BASE_TEMPLATE = getattr(settings, "BASE_TEMPLATE", "grow/base.html")
USE_BOOTSTRAP = getattr(settings, "USE_BOOTSTRAP", False)
LOGIN_REQUIRED = getattr(settings, "LOGIN_REQUIRED", False)

GROW_BUILTIN_TEMPLATES = {
    'grow/strain': 'grow/strain/index.html',
    'grow/strain/breeder': 'grow/strain/breeder_detail.html',
    'grow/strain/breeder/create': 'grow/strain/breeder_create.html',
    'grow/strain/breeder/update': 'grow/strain/breeder_update.html',
    'grow/strain/create': 'grow/strain/strain_create.html',
    'grow/strain/detail': 'grow/strain/strain_detail.html',
    'grow/strain/index': 'grow/strain/index.html',
    'grow/strain/search': 'grow/strain/strain_search.html',
    'grow/strain/update': 'grow/strain/strain_update.html',
    'grow/strain/strain/search': 'grow/strain/search.html',
}

GROW_TEMPLATES = getattr('settings', 'GROW_TEMPLATES', None)
if not GROW_TEMPLATES:
    GROW_TEMPLATES = GROW_BUILTIN_TEMPLATES
else:
    for _id, _template_name in GROW_BUILTIN_TEMPLATES.items():
        GROW_TEMPLATES.setdefault(_id, _template_name)
    del _id, _template_name
