from django.conf import settings
from .growapi.settings import *  # noqa

BASE_TEMPLATE = getattr(settings, "BASE_TEMPLATE", "grow/base.html")
USE_BOOTSTRAP = getattr(settings, "USE_BOOTSTRAP", False)
LOGIN_REQUIRED = getattr(settings, "LOGIN_REQUIRED", False)
GROW_SITE_TITLE = getattr(settings, "GROW_SITE_TITLE", getattr(settings, "SITE_TITLE", "Grow"))
GROW_HEAD_TITLE = getattr(settings, "GROW_HEAD_TITLE", getattr(settings, "HEAD_TITLE", GROW_SITE_TITLE))

GROW_BUILTIN_TEMPLATES = {
    'grow/breeder/create': 'grow/strain/breeder_create.html',
    'grow/breeder/delete': 'grow/strain/breeder_delete.html',
    'grow/breeder/detail': 'grow/strain/breeder_detail.html',
    'grow/breeder/hx-delete': 'grow/strain/hx_breeder_delete.html',
    'grow/breeder/update': 'grow/strain/breeder_update.html',
    'grow/index': 'grow/index/index.html',
    'grow/index/sanitize-date-day': 'grow/index/hx_sanitize_date_day.html',
    'grow/strain': 'grow/strain/index.html',
    'grow/strain/add_to_stock': 'grow/strain/strain_add_to_stock.html',

    'grow/strain/create': 'grow/strain/strain_create.html',
    'grow/strain/delete': 'grow/strain/strain_delete.html',
    'grow/strain/detail': 'grow/strain/strain_detail.html',
    'grow/strain/hx-add_to_stock': 'grow/strain/hx_strain_add_to_stock.html',
    'grow/strain/hx-delete': 'grow/strain/hx_strain_delete.html',
    'grow/strain/hx-remove_from_stock': 'grow/strain/hx_strain_remove_from_stock.html',
    'grow/strain/hx-remove_from_stock_invalid': 'grow/strain/hx_strain_remove_from_stock_invalid.html',
    'grow/strain/hx-strain_in_stock_update': 'grow/strain/hx_strain_in_stock_update.html',
    'grow/strain/hx-search': 'grow/strain/hx_strain_search.html',
    'grow/strain/index': 'grow/strain/index.html',
    'grow/strain/remove_from_stock': 'grow/strain/strain_remove_from_stock.html',
    'grow/strain/remove_from_stock_invalid': 'grow/strain/strain_remove_from_stock_invalid.html',
    'grow/strain/search': 'grow/strain/strain_search.html',
    'grow/strain/search_result': 'grow/strain/search.html',
    'grow/strain/update': 'grow/strain/strain_update.html',

    'grow/utils/hx_select_date_days_sanitize': 'grow/utils/hx_select_date_days_sanitize.html'
}

BS_GROW_BUILTIN_TEMPLATES = {
    'grow/breeder/create': 'grow/strain/bs_breeder_create.html',
    'grow/breeder/delete': 'grow/strain/bs_breeder_delete.html',
    'grow/breeder/detail': 'grow/strain/bs_breeder_detail.html',
    'grow/breeder/hx-delete': 'grow/strain/bs_hx_breeder_delete.html',
    'grow/breeder/update': 'grow/strain/bs_breeder_update.html',
    'grow/index': 'grow/index/index.html',
    'grow/index/sanitize-date-day': 'grow/index/hx_sanitize_date_day.html',
    'grow/strain': 'grow/strain/index.html',
    'grow/strain/add_to_stock': 'grow/strain/strain_add_to_stock.html',

    'grow/strain/create': 'grow/strain/strain_create.html',
    'grow/strain/delete': 'grow/strain/strain_delete.html',
    'grow/strain/detail': 'grow/strain/strain_detail.html',
    'grow/strain/hx-add_to_stock': 'grow/strain/hx_strain_add_to_stock.html',
    'grow/strain/hx-delete': 'grow/strain/hx_strain_delete.html',
    'grow/strain/hx-remove_from_stock': 'grow/strain/hx_strain_remove_from_stock.html',
    'grow/strain/hx-remove_from_stock_invalid': 'grow/strain/hx_strain_remove_from_stock_invalid.html',
    'grow/strain/hx-strain_in_stock_update': 'grow/strain/hx_strain_in_stock_update.html',
    'grow/strain/hx-search': 'grow/strain/hx_strain_search.html',
    'grow/strain/index': 'grow/strain/index.html',
    'grow/strain/remove_from_stock': 'grow/strain/strain_remove_from_stock.html',
    'grow/strain/remove_from_stock_invalid': 'grow/strain/strain_remove_from_stock_invalid.html',
    'grow/strain/search': 'grow/strain/strain_search.html',
    'grow/strain/search_result': 'grow/strain/search.html',
    'grow/strain/update': 'grow/strain/strain_update.html',
    'grow/utils/hx_select_date_days_sanitize': 'grow/utils/hx_select_date_days_sanitize.html'
}

GROW_TEMPLATES = getattr('settings', 'GROW_TEMPLATES', None)
if not GROW_TEMPLATES:
    if USE_BOOTSTRAP:
        GROW_TEMPLATES = BS_GROW_BUILTIN_TEMPLATES
    else:
        GROW_TEMPLATES = GROW_BUILTIN_TEMPLATES
else:
    GROW_TEMPLATES = dict(GROW_TEMPLATES)
    if USE_BOOTSTRAP:
        for _id, _template_name in BS_GROW_BUILTIN_TEMPLATES.items():
            GROW_TEMPLATES.setdefault(_id, _template_name)
    else:
        for _id, _template_name in GROW_BUILTIN_TEMPLATES.items():
            GROW_TEMPLATES.setdefault(_id, _template_name)
    del _id, _template_name

SITE_TITLE = getattr(settings, "SITE_TITLE", "Grow")
