from django.conf import settings
from .growapi.settings import *  # noqa

USE_BOOTSTRAP = getattr(settings, "USE_BOOTSTRAP", True)
BASE_TEMPLATE = getattr(settings, "BASE_TEMPLATE", "grow/bs_base.html") # if USE_BOOTSTRAP else "grow/base.html")
LOGIN_REQUIRED = getattr(settings, "LOGIN_REQUIRED", False)
GROW_SITE_TITLE = getattr(settings, "GROW_SITE_TITLE", getattr(settings, "SITE_TITLE", "Grow"))
GROW_HEAD_TITLE = getattr(settings, "GROW_HEAD_TITLE", getattr(settings, "HEAD_TITLE", GROW_SITE_TITLE))
GROW_IS_MAIN_APP = getattr(settings, "GROW_IS_MAIN_APP", False)

GROW_BUILTIN_TEMPLATES = {
    # breeder templates
    'grow/breeder/create': 'grow/strain/breeder_create.html',
    'grow/breeder/delete': 'grow/strain/breeder_delete.html',
    'grow/breeder/detail': 'grow/strain/breeder_detail.html',
    'grow/breeder/translation': 'grow/strain/breeder_translation.html',
    'grow/breeder/hx-delete': 'grow/strain/hx_breeder_delete.html',
    'grow/breeder/hx-breeder-filter': 'grow/strain/hx_breeder_filter.html',
    'grow/breeder/hx-translation': 'grow/strain/hx_breeder_translation.html',
    'grow/breeder/update': 'grow/strain/breeder_update.html',

    # home
    'grow/index': 'grow/index/index.html',

    # location templates
    'grow/location/index': 'grow/location/index.html',
    'grow/location/create': 'grow/location/create.html',
    'grow/location/update': 'grow/location/update.html',
    'grow/location/delete': 'grow/location/delete.html',
    'grow/location/detail': 'grow/location/detail.html',
    'grow/location/hx-type-change': 'grow/location/hx_locationtype_change.html',
    'grow/location/hx-delete': 'grow/location/hx_delete.html',

    # strain templates
    'grow/strain': 'grow/strain/index.html',
    'grow/strain/add_to_stock': 'grow/strain/strain_add_to_stock.html',
    'grow/strain/create': 'grow/strain/strain_create.html',
    'grow/strain/comment_create': 'grow/strain/strain_comment_create.html',
    'grow/strain/comment_update': 'grow/strain/strain_comment_update.html',
    'grow/strain/delete': 'grow/strain/strain_delete.html',
    'grow/strain/detail': 'grow/strain/strain_detail.html',
    'grow/strain/gallery': 'grow/strain/strain_gallery.html',
    'grow/strain/gallery_slides': 'grow/strain/strain_gallery_slides.html',
    'grow/strain/hx-add_to_stock': 'grow/strain/hx_strain_add_to_stock.html',
    'grow/strain/hx-delete': 'grow/strain/hx_strain_delete.html',
    'grow/strain/hx-strain-filter': 'grow/strain/hx_strain_filter.html',
    'grow/strain/hx-remove_from_stock': 'grow/strain/hx_strain_remove_from_stock.html',
    'grow/strain/hx-remove_from_stock_invalid': 'grow/strain/hx_strain_remove_from_stock_invalid.html',
    'grow/strain/hx-strain_in_stock_update': 'grow/strain/hx_strain_in_stock_update.html',
    'grow/strain/hx-translation': 'grow/strain/hx_strain_translation.html',
    'grow/strain/hx-search': 'grow/strain/hx_strain_search.html',
    'grow/strain/image_upload': 'grow/strain/strain_image_upload.html',
    'grow/strain/index': 'grow/strain/index.html',
    'grow/strain/remove_from_stock': 'grow/strain/strain_remove_from_stock.html',
    'grow/strain/remove_from_stock_invalid': 'grow/strain/strain_remove_from_stock_invalid.html',
    'grow/strain/strain_search_results': 'grow/strain/strain_search_results.html',
    'grow/strain/translation': 'grow/strain/strain_translation.html',
    'grow/strain/update': 'grow/strain/strain_update.html',

    # location views
    'grow/location/create': 'grow/location/create.html',
    'grow/location/delete': 'grow/location/delete.html',
    'grow/location/detail': 'grow/location/detail.html',
    'grow/location/hx-delete': 'grow/location/hx_delete.html',

    # growlog views
    'grow/growlog/create': 'grow/growlog/growlog_create.html',
    'grow/growlog/delete': 'grow/growlog/growlog_delete.html',
    'grow/growlog/detail': 'grow/growlog/growlog_detail.html',
    'grow/growlog/entry_image_upload': 'grow/growlog/entry_image_upload.html',
    'grow/growlog/update': 'grow/growlog/growlog_update.html',
    'grow/growlog/entry_image_delete': 'grow/growlog/entry_image_delete.html',
    'grow/growlog/hx-entry-image-delete': 'grow/growlog/hx_entry_image_delete.html',
    'grow/growlog/hx-entry-image-upload': 'grow/growlog/hx_entry_image_upload.html',
    'grow/growlog/hx-delete': 'grow/growlog/hx_delete.html',
    'grow/growlog/entry_create': 'grow/growlog/entry_create.html',
    'grow/growlog/entry_delete': 'grow/growlog/entry_delete.html',
    'grow/growlog/entry_update': 'grow/growlog/entry_update.html',
    'grow/growlog/hx-entry-delete': 'grow/growlog/hx_entry_delete.html',

    # user views
    'grow/user/info': 'grow/user/info.html',

    # utils
    'grow/utils/hx_select_date_days_sanitize': 'grow/utils/hx_select_date_days_sanitize.html'
}

GROW_TEMPLATES = getattr('settings', 'GROW_TEMPLATES', None)
if not GROW_TEMPLATES:
    GROW_TEMPLATES = GROW_BUILTIN_TEMPLATES
else:
    GROW_TEMPLATES = dict(GROW_TEMPLATES)
    for _id, _template_name in GROW_BUILTIN_TEMPLATES.items():
        GROW_TEMPLATES.setdefault(_id, _template_name)
    del _id, _template_name


SITE_TITLE = getattr(settings, "SITE_TITLE", "Grow")
