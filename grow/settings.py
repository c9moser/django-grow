from django.conf import settings
from .growapi.settings import *  # noqa

USE_BOOTSTRAP = getattr(settings, "USE_BOOTSTRAP", True)
BASE_TEMPLATE = getattr(settings, "BASE_TEMPLATE", "grow/bs_base.html") # if USE_BOOTSTRAP else "grow/base.html")
LOGIN_REQUIRED = getattr(settings, "LOGIN_REQUIRED", False)
GROW_SITE_TITLE = getattr(settings, "GROW_SITE_TITLE", getattr(settings, "SITE_TITLE", "Grow"))
GROW_HEAD_TITLE = getattr(settings, "GROW_HEAD_TITLE", getattr(settings, "HEAD_TITLE", GROW_SITE_TITLE))
GROW_IS_MAIN_APP = getattr(settings, "GROW_IS_MAIN_APP", False)

GROW_BUILTIN_BREEDER_TEMPLATES = {
    'grow/breeder': 'grow/html/breeder/index.html',
    'grow/breeder/create': 'grow/html/breeder/create.html',
    'grow/breeder/delete': 'grow/html/breeder/delete.html',
    'grow/breeder/detail': 'grow/html/breeder/detail.html',
    'grow/breeder/translation': 'grow/html/breeder/translation.html',
    'grow/breeder/hx/delete': 'grow/html/breeder/hx/delete.html',
    'grow/breeder/hx/filter': 'grow/html/breeder/hx/filter.html',
    'grow/breeder/hx/strains': 'grow/html/breeder/hx/strains.html',
    'grow/breeder/hx/translation': 'grow/html/breeder/hx/translation.html',
    'grow/breeder/update': 'grow/html/breeder/update.html',
    'grow/breeder/form': 'grow/html/breeder/form.html',
}

GROW_BUILTIN_BS_BREEDER_TEMPLATES = {
    'grow/breeder': 'grow/bootstrap/breeder/index.html',
    'grow/breeder/create': 'grow/bootstrap/breeder/create.html',
    'grow/breeder/delete': 'grow/bootstrap/breeder/delete.html',
    'grow/breeder/detail': 'grow/bootstrap/breeder/detail.html',
    'grow/breeder/translation': 'grow/bootstrap/breeder/translation.html',
    'grow/breeder/hx/delete': 'grow/bootstrap/breeder/hx/delete.html',
    'grow/breeder/hx/filter': 'grow/bootstrap/breeder/hx/filter.html',
    'grow/breeder/hx/strains': 'grow/bootstrap/breeder/hx/strains.html',
    'grow/breeder/hx/translation': 'grow/bootstrap/breeder/hx/translation.html',
    'grow/breeder/update': 'grow/bootstrap/breeder/update.html',
    'grow/breeder/form': 'grow/bootstrap/breeder/form.html',
}

GROW_BUILTIN_STRAIN_TEMPLATES = {
    # strain templates
    'grow/strain': 'grow/html/strain/index.html',
    'grow/strain/create': 'grow/html/strain/create.html',
    'grow/strain/delete': 'grow/html/strain/delete.html',
    'grow/strain/form': 'grow/html/strain/form.html',
    'grow/strain/gallery': 'grow/html/strain/gallery/gallery.html',
    'grow/strain/gallery/slides': 'grow/html/strain/gallery/slides.html',
    'grow/strain/hx/delete': 'grow/html/strain/hx/delete.html',
    'grow/strain/hx/search': 'grow/html/strain/hx/search.html',
    'grow/strain/strain': 'grow/html/strain/detail.html',
    'grow/strain/strain/add_to_stock': 'grow/html/strain/add_to_stock.html',
    'grow/strain/strain/add_to_stock2': 'grow/html/strain/add_to_stock2.html',
    'grow/strain/strain/comment_create': 'grow/html/strain/comment/create.html',
    'grow/strain/strain/comment_update': 'grow/html/strain/comment/update.html',
    'grow/strain/strain/form': 'grow/html/strain/form.html',
    'grow/strain/strain/hx/add_to_stock': 'grow/html/strain/hx/add_to_stock.html',
    'grow/strain/strain/hx/add_to_stock2': 'grow/html/strain/hx/add_to_stock2.html',
    'grow/strain/strain/hx/add_to_stock_dialog': 'grow/html/strain/hx/dialog.html',
    'grow/strain/strain/hx/filter': 'grow/html/strain/hx/filter.html',
    'grow/strain/strain/hx/growlogs': 'grow/html/strain/hx/growlogs.html',
    'grow/strain/strain/hx/translation': 'grow/html/strain/hx/translation.html',
    'grow/strain/strain/in_stock/hx/add': 'grow/html/strain/hx/add_to_stock.html',
    'grow/strain/strain/in_stock/hx/remove': 'grow/html/strain/hx/remove_from_stock.html',
    'grow/strain/strain/in_stock/hx/remove_invalid': 'grow/html/strain/hx/remove_from_stock_invalid.html',
    'grow/strain/strain/in_stock/hx/notes': 'grow/html/strain/hx/in_stock_notes.html',
    'grow/strain/strain/in_stock/hx/update': 'grow/html/strain/hx/in_stock_update.html',

    'grow/strain/strain/image_upload': 'grow/html/strain/image/upload.html',
    'grow/strain/strain/remove_from_stock': 'grow/html/strain/remove_from_stock.html',
    'grow/strain/strain/remove_from_stock_invalid': 'grow/html/remove_from_stock_invalid.html',
    'grow/strain/strain_search_results': 'grow/html/strain/search_results.html',
    'grow/strain/strain/translation': 'grow/html/strain/translation.html',
    'grow/strain/strain/update': 'grow/html/strain/update.html',
}

GROW_BUILTIN_BS_STRAIN_TEMPLATES = {
    # strain templates
    'grow/strain': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain'],
    'grow/strain/create': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/create'],
    'grow/strain/delete': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/delete'],
    'grow/strain/form': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/form'],
    'grow/strain/gallery': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/gallery'],
    'grow/strain/gallery/slides': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/gallery/slides'],
    'grow/strain/hx/delete': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/hx/delete'],
    'grow/strain/hx/search': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/hx/search'],
    'grow/strain/strain': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/strain'],
    'grow/strain/strain/add_to_stock': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/strain/add_to_stock'],
    'grow/strain/strain/add_to_stock2': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/strain/add_to_stock2'],
    'grow/strain/strain/comment_create': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/strain/comment_create'],
    'grow/strain/strain/comment_update': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/strain/comment_update'],
    'grow/strain/strain/form': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/strain/form'],
    'grow/strain/strain/hx/add_to_stock': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/strain/hx/add_to_stock'],
    'grow/strain/strain/hx/add_to_stock2': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/strain/hx/add_to_stock2'],
    'grow/strain/strain/hx/add_to_stock_dialog': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/strain/hx/add_to_stock_dialog'],
    'grow/strain/strain/hx/filter': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/strain/hx/filter'],
    'grow/strain/strain/hx/growlogs': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/strain/hx/growlogs'],
    'grow/strain/strain/hx/translation': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/strain/hx/translation'],
    'grow/strain/strain/in_stock/hx/add': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/strain/in_stock/hx/add'],
    'grow/strain/strain/in_stock/hx/remove': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/strain/in_stock/hx/remove'],
    'grow/strain/strain/in_stock/hx/remove_invalid': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/strain/in_stock/hx/remove_invalid'],
    'grow/strain/strain/in_stock/hx/notes': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/strain/in_stock/hx/notes'],
    'grow/strain/strain/in_stock/hx/update': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/strain/in_stock/hx/update'],

    'grow/strain/strain/image_upload': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/strain/image_upload'],
    'grow/strain/strain/remove_from_stock': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/strain/remove_from_stock'],
    'grow/strain/strain/remove_from_stock_invalid': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/strain/remove_from_stock_invalid'],
    'grow/strain/strain_search_results': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/strain_search_results'],
    'grow/strain/strain/translation': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/strain/translation'],
    'grow/strain/strain/update': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/strain/update'],
}


GROW_BUILTIN_LOCATION_TEMPLATES = {
    # location templates
    'grow/location/index': 'grow/html/location/index.html',
    'grow/location/create': 'grow/html/location/create.html',
    'grow/location/update': 'grow/html/location/update.html',
    'grow/location/delete': 'grow/html/location/delete.html',
    'grow/location/detail': 'grow/html/location/detail.html',
    'grow/location/form': 'grow/html/location/form.html',
    'grow/location/hx-type-change': 'grow/html/location/hx_locationtype_change.html',
    'grow/location/hx-delete': 'grow/html/location/hx_delete.html',
}

GROW_BUILTIN_BS_LOCATION_TEMPLATES = {
    # location templates
    'grow/location/index': GROW_BUILTIN_LOCATION_TEMPLATES['grow/location/index'],
    'grow/location/create': GROW_BUILTIN_LOCATION_TEMPLATES['grow/location/create'],
    'grow/location/update': GROW_BUILTIN_LOCATION_TEMPLATES['grow/location/update'],
    'grow/location/delete': GROW_BUILTIN_LOCATION_TEMPLATES['grow/location/delete'],
    'grow/location/detail': GROW_BUILTIN_LOCATION_TEMPLATES['grow/location/detail'],
    'grow/location/form': GROW_BUILTIN_LOCATION_TEMPLATES['grow/location/form'],
    'grow/location/hx-type-change': GROW_BUILTIN_LOCATION_TEMPLATES['grow/location/hx-type-change'],
    'grow/location/hx-delete': GROW_BUILTIN_LOCATION_TEMPLATES['grow/location/hx-delete'],
}

GROW_BUILTIN_SIS_TEMPLATES = {
    'grow/seeds_in_stock': 'grow/html/seeds_in_stock/my_seeds_in_stock.html',
    'grow/seeds_in_stock/add': 'grow/html/seeds_in_stock/add.html',
    'grow/seeds_in_stock/remove': 'grow/html/seeds_in_stock/remove.html',
    'grow/seeds_in_stock/remove_invalid': 'grow/html/seeds_in_stock/remove_invalid.html',
    'grow/seeds_in_stock/hx/add': 'grow/html/seeds_in_stock/hx/add.html',
    'grow/seeds_in_stock/hx/remove': 'grow/html/seeds_in_stock/hx/remove.html',
    'grow/seeds_in_stock/hx/remove_invalid': 'grow/html/seeds_in_stock/hx/remove_invalid.html',
    'grow/seeds_in_stock/hx/info': 'grow/html/seeds_in_stock/hx/info.html',
    'grow/seeds_in_stock/hx/dialog': 'grow/html/seeds_in_stock/hx/dialog.html',
    'grow/seeds_in_stock/hx/info': 'grow/html/seeds_in_stock/hx/info.html',
}

GROW_BUILTIN_BS_SIS_TEMPLATES = {
    'grow/seeds_in_stock': GROW_BUILTIN_SIS_TEMPLATES['grow/seeds_in_stock'],
    'grow/seeds_in_stock/add': GROW_BUILTIN_SIS_TEMPLATES['grow/seeds_in_stock/add'],
    'grow/seeds_in_stock/remove': GROW_BUILTIN_SIS_TEMPLATES['grow/seeds_in_stock/remove'],
    'grow/seeds_in_stock/remove_invalid': GROW_BUILTIN_SIS_TEMPLATES['grow/seeds_in_stock/remove_invalid'],
    'grow/seeds_in_stock/hx/add': GROW_BUILTIN_SIS_TEMPLATES['grow/seeds_in_stock/hx/add'],
    'grow/seeds_in_stock/hx/remove': GROW_BUILTIN_SIS_TEMPLATES['grow/seeds_in_stock/hx/remove'],
    'grow/seeds_in_stock/hx/remove_invalid': GROW_BUILTIN_SIS_TEMPLATES['grow/seeds_in_stock/hx/remove_invalid'],
    'grow/seeds_in_stock/hx/info': GROW_BUILTIN_SIS_TEMPLATES['grow/seeds_in_stock/hx/info'],
    'grow/seeds_in_stock/hx/dialog': GROW_BUILTIN_SIS_TEMPLATES['grow/seeds_in_stock/hx/dialog'],
    'grow/seeds_in_stock/hx/info': GROW_BUILTIN_SIS_TEMPLATES['grow/seeds_in_stock/hx/info'],
}

GROW_BUILTIN_GROWLOG_TEMPLATES = {
    'grow/growlog/create': 'grow/html/growlog/growlog/create.html',
    'grow/growlog/delete': 'grow/html/growlog/growlog/delete.html',
    'grow/growlog/detail': 'grow/html/growlog/growlog/detail.html',
    'grow/growlog/update': 'grow/html/growlog/growlog/update.html',
    'grow/growlog/form': 'grow/html/growlog/growlog/form.html',

    'grow/growlog/entry/image_delete': 'grow/html/growlog/entry/image_delete.html',
    'grow/growlog/entry/image_upload': 'grow/html/growlog/entry/image_upload.html',
    'grow/growlog/entry/create': 'grow/html/growlog/entry/form.html',
    'grow/growlog/entry/update': 'grow/html/growlog/entry/form.html',
    'grow/growlog/entry/delete': 'grow/html/growlog/entry/delete.html',
    'grow/growlog/entry/form': 'grow/html/growlog/entry/form.html',
    'grow/growlog/entry/image/upload': 'grow/html/growlog/entry/image/upload.html',
    'grow/growlog/entry/image/delete': 'grow/html/growlog/entry/image/delete.html',
    'grow/growlog/entry/image/update': 'grow/html/growlog/entry/image/update.html',
    'grow/growlog/entry/image/hx/delete': 'grow/html/growlog/entry/image/hx/delete.html',
    'grow/growlog/entry/image/hx/upload': 'grow/html/growlog/entry/image/hx/upload.html',
    'grow/growlog/entry/image/hx/update': 'grow/html/growlog/entry/image/hx/update.html',
    'grow/growlog/entry/timestamp': 'grow/html/growlog/entry/timestamp.html',
    'grow/growlog/entry/hx/delete': 'grow/html/growlog/entry/hx/delete.html',
    'grow/growlog/entry/hx/create': 'grow/html/growlog/entry/hx/form_dialog.html',
    'grow/growlog/entry/hx/update': 'grow/html/growlog/entry/hx/form_dialog.html',
    'grow/growlog/forbidden': 'grow/html/growlog/forbidden.html',
    'grow/growlog/hx/active_info' : 'grow/html/growlog/hx/active_info.html',
    'grow/growlog/hx/finished_info' : 'grow/html/growlog/hx/finished_info.html',
    'grow/growlog/hx/strains_grown': 'grow/html/growlog/hx/strains_grown.html',
    'grow/growlog/growlog/hx/entries': 'grow/html/growlog/growlog/hx/entries.html',
    'grow/growlog/growlog/hx/seeds_add': 'grow/html/growlog/growlog/hx/add_seeds.html',
    'grow/growlog/growlog/hx/description': 'grow/html/growlog/growlog/hx/description.html',
    'grow/growlog/growlog/hx/edit_notes': 'grow/html/growlog/growlog/hx/edit_notes.html',
    'grow/growlog/growlog/hx/notes': 'grow/html/growlog/growlog/hx/notes.html',
    'grow/growlog/growlog/hx/edit_description': 'grow/html/growlog/growlog/hx/edit_description.html',
    'grow/growlog/growlog/hx/strains':  'grow/html/growlog/growlog/hx/strains.html',
    'grow/growlog/growlog/hx/add_plants':  'grow/html/growlog/growlog/hx/add_plants.html',
    'grow/growlog/growlog/hx/remove_plants':  'grow/html/growlog/growlog/hx/remove_plants.html',
    'grow/growlog/growlog/hx/add_strain':  'grow/html/growlog/growlog/hx/add_strain.html',
    'grow/growlog/growlog/hx/delete_strain':  'grow/html/growlog/growlog/hx/delete_strain.html',
    'grow/growlog/my_growlogs': 'grow/html/growlog/my_growlogs.html',
    'grow/growlog/strains_grown': 'grow/html/growlog/strains_grown.html',
}

GROW_BUILTIN_BS_GROWLOG_TEMPLATES = {
    'grow/growlog/create': GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/create'],
    'grow/growlog/delete': GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/delete'],
    'grow/growlog/detail': GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/detail'],
    'grow/growlog/update': GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/update'],
    'grow/growlog/form': GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/form'],

    'grow/growlog/entry/image_delete': GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/entry/image_delete'],
    'grow/growlog/entry/image_upload': GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/entry/image_upload'],
    'grow/growlog/entry/create': GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/entry/create'],
    'grow/growlog/entry/update': GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/entry/update'],
    'grow/growlog/entry/delete': GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/entry/delete'],
    'grow/growlog/entry/form': GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/entry/form'],
    'grow/growlog/entry/image/upload': GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/entry/image/upload'],
    'grow/growlog/entry/image/delete': GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/entry/image/delete'],
    'grow/growlog/entry/image/update': GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/entry/image/update'],
    'grow/growlog/entry/image/hx/delete': GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/entry/image/hx/delete'],
    'grow/growlog/entry/image/hx/upload': GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/entry/image/hx/upload'],
    'grow/growlog/entry/image/hx/update': GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/entry/image/hx/update'],
    'grow/growlog/entry/timestamp': GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/entry/timestamp'],
    'grow/growlog/entry/hx/delete': GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/entry/hx/delete'],
    'grow/growlog/entry/hx/create': GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/entry/hx/create'],
    'grow/growlog/entry/hx/update': GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/entry/hx/update'],
    'grow/growlog/forbidden': GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/forbidden'],
    'grow/growlog/hx/active_info' : GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/hx/active_info'],
    'grow/growlog/hx/finished_info' : GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/hx/finished_info'],
    'grow/growlog/hx/strains_grown': GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/hx/strains_grown'],
    'grow/growlog/growlog/hx/entries': GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/growlog/hx/entries'],
    'grow/growlog/growlog/hx/seeds_add': GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/growlog/hx/seeds_add'],
    'grow/growlog/growlog/hx/description': GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/growlog/hx/description'],
    'grow/growlog/growlog/hx/edit_notes': GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/growlog/hx/edit_notes'],
    'grow/growlog/growlog/hx/notes': GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/growlog/hx/notes'],
    'grow/growlog/growlog/hx/edit_description': GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/growlog/hx/edit_description'],
    'grow/growlog/growlog/hx/strains':  GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/growlog/hx/strains'],
    'grow/growlog/growlog/hx/add_plants':  GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/growlog/hx/add_plants'],
    'grow/growlog/growlog/hx/remove_plants':  GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/growlog/hx/remove_plants'],
    'grow/growlog/growlog/hx/add_strain':  GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/growlog/hx/add_strain'],
    'grow/growlog/growlog/hx/delete_strain':  GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/growlog/hx/delete_strain'],
    'grow/growlog/my_growlogs': GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/my_growlogs'],
    'grow/growlog/strains_grown': GROW_BUILTIN_GROWLOG_TEMPLATES['grow/growlog/strains_grown'],
}

GROW_BUILTIN_USER_TEMPLATES = {
    'grow/user/hx-add_seeds_to_stock': 'grow/html/user/hx_add_seeds_to_stock.html',
    'grow/user/hx-remove_seeds_from_stock': 'grow/html/user/hx_remove_seeds_from_stock.html',
    'grow/user/info': 'grow/html/user/info.html',
}

GROW_BUILTIN_BS_USER_TEMPLATES = {
    'grow/user/hx-add_seeds_to_stock': GROW_BUILTIN_USER_TEMPLATES['grow/user/hx-add_seeds_to_stock'],
    'grow/user/hx-remove_seeds_from_stock': GROW_BUILTIN_USER_TEMPLATES['grow/user/hx-remove_seeds_from_stock'],
    'grow/user/info': GROW_BUILTIN_USER_TEMPLATES['grow/user/info'],
}

GROW_BUILTIN_UTILS_TEMPLATES = {
    'grow/utils/hx_select_date_days_sanitize': 'grow/html/utils/hx_select_date_days_sanitize.html',
    'grow/utils/paginator': 'grow/html/utils/paginator.html',
}

GROW_BUILTIN_BS_UTILS_TEMPLATES = {
    'grow/utils/hx_select_date_days_sanitize': GROW_BUILTIN_UTILS_TEMPLATES['grow/utils/hx_select_date_days_sanitize'],
}

GROW_BUILTIN_TEMPLATES = {
    # home
    'grow/index': 'grow/html/index/index.html',


}
GROW_BUILTIN_TEMPLATES.update(GROW_BUILTIN_BREEDER_TEMPLATES)
GROW_BUILTIN_TEMPLATES.update(GROW_BUILTIN_STRAIN_TEMPLATES)
GROW_BUILTIN_TEMPLATES.update(GROW_BUILTIN_LOCATION_TEMPLATES)
GROW_BUILTIN_TEMPLATES.update(GROW_BUILTIN_SIS_TEMPLATES)
GROW_BUILTIN_TEMPLATES.update(GROW_BUILTIN_GROWLOG_TEMPLATES)
GROW_BUILTIN_TEMPLATES.update(GROW_BUILTIN_USER_TEMPLATES)
GROW_BUILTIN_TEMPLATES.update(GROW_BUILTIN_UTILS_TEMPLATES)

GROW_BUILTIN_BS_TEMPLATES = {
    #index
    'grow/index': 'grow/bootstrap/index/index.html',
    # user views
    'grow/user/hx-add_seeds_to_stock': 'grow/user/hx_add_seeds_to_stock.html',
    'grow/user/hx-remove_seeds_from_stock': 'grow/user/hx_remove_seeds_from_stock.html',
    'grow/user/info': 'grow/user/info.html',

    # utils
    'grow/utils/hx_select_date_days_sanitize': 'grow/utils/hx_select_date_days_sanitize.html'
}
GROW_BUILTIN_BS_TEMPLATES.update(GROW_BUILTIN_BS_BREEDER_TEMPLATES)
GROW_BUILTIN_BS_TEMPLATES.update(GROW_BUILTIN_BS_STRAIN_TEMPLATES)
GROW_BUILTIN_BS_TEMPLATES.update(GROW_BUILTIN_BS_LOCATION_TEMPLATES)
GROW_BUILTIN_BS_TEMPLATES.update(GROW_BUILTIN_BS_SIS_TEMPLATES)
GROW_BUILTIN_BS_TEMPLATES.update(GROW_BUILTIN_BS_GROWLOG_TEMPLATES)
GROW_BUILTIN_BS_TEMPLATES.update(GROW_BUILTIN_BS_USER_TEMPLATES)
GROW_BUILTIN_BS_TEMPLATES.update(GROW_BUILTIN_BS_UTILS_TEMPLATES)


GROW_TEMPLATES = getattr('settings', 'GROW_TEMPLATES', None)
if not GROW_TEMPLATES:
    if USE_BOOTSTRAP:
        GROW_TEMPLATES = GROW_BUILTIN_BS_TEMPLATES
    else:
        GROW_TEMPLATES = GROW_BUILTIN_TEMPLATES
else:
    GROW_TEMPLATES = dict(GROW_TEMPLATES)
    if USE_BOOTSTRAP:
         for _id, _template_name in GROW_BUILTIN_BS_TEMPLATES.items():
            GROW_TEMPLATES.setdefault(_id, _template_name)
    else:
        for _id, _template_name in GROW_BUILTIN_TEMPLATES.items():
            GROW_TEMPLATES.setdefault(_id, _template_name)
    del _id, _template_name


SITE_TITLE = getattr(settings, "SITE_TITLE", "Grow")

def GROW_USER_SETTINGS(request):
    if not request.user.is_authenticated:
        return None

    from .growapi.models import GrowUserSettings
    try:
        return request.user.grow_settings
    except:
        return GrowUserSettings.objects.create(user=request.user,
                                               paginate=GROW_PAGINATE,
                                               growlog_paginate=GROW_GROWLOG_PAGINATE)
