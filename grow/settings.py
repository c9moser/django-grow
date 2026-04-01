from django.conf import settings
from .growapi.settings import *  # noqa

USE_BOOTSTRAP = getattr(settings, "USE_BOOTSTRAP", True)
BASE_TEMPLATE = getattr(settings, "BASE_TEMPLATE", "grow/bs_base.html") # if USE_BOOTSTRAP else "grow/base.html")
LOGIN_REQUIRED = getattr(settings, "LOGIN_REQUIRED", False)
GROW_SITE_TITLE = getattr(settings, "GROW_SITE_TITLE", getattr(settings, "SITE_TITLE", "Grow"))
GROW_HEAD_TITLE = getattr(settings, "GROW_HEAD_TITLE", getattr(settings, "HEAD_TITLE", GROW_SITE_TITLE))
GROW_IS_MAIN_APP = getattr(settings, "GROW_IS_MAIN_APP", False)

GROW_BUILTIN_BREEDER_TEMPLATES = {
    'grow/breeder/create': 'grow/breeder/create.html',
    'grow/breeder/delete': 'grow/breeder/delete.html',
    'grow/breeder/detail': 'grow/breeder/detail.html',
    'grow/breeder/translation': 'grow/breeder/translation.html',
    'grow/breeder/hx/delete': 'grow/breeder/hx/delete.html',
    'grow/breeder/hx/filter': 'grow/breeder/hx/filter.html',
    'grow/breeder/hx/translation': 'grow/breeder/hx/translation.html',
    'grow/breeder/update': 'grow/breeder/update.html',
    'grow/breeder/form': 'grow/breeder/form.html',
}

GROW_BUILTIN_BS_BREEDER_TEMPLATES = {
    'grow/breeder/create': 'grow/bootstrap/breeder/create.html',
    'grow/breeder/delete': GROW_BUILTIN_BREEDER_TEMPLATES['grow/breeder/delete'],
    'grow/breeder/detail': GROW_BUILTIN_BREEDER_TEMPLATES['grow/breeder/detail'],
    'grow/breeder/translation': GROW_BUILTIN_BREEDER_TEMPLATES['grow/breeder/translation'],
    'grow/breeder/hx/delete': GROW_BUILTIN_BREEDER_TEMPLATES['grow/breeder/hx/delete'],
    'grow/breeder/hx/filter': GROW_BUILTIN_BREEDER_TEMPLATES['grow/breeder/hx/filter'],
    'grow/breeder/hx/translation': GROW_BUILTIN_BREEDER_TEMPLATES['grow/breeder/hx/translation'],
    'grow/breeder/update': GROW_BUILTIN_BREEDER_TEMPLATES['grow/breeder/update'],
    'grow/breeder/form': 'grow/bootstrap/breeder/form.html',
}

GROW_BUILTIN_STRAIN_TEMPLATES = {
    # strain templates
    'grow/strain': 'grow/strain/index.html',
    'grow/strain/create': 'grow/strain/strain/create.html',
    'grow/strain/delete': 'grow/strain/strain/delete.html',
    'grow/strain/gallery': 'grow/strain/strain/gallery/gallery.html',
    'grow/strain/gallery/slides': 'grow/strain/strain/gallery/slides.html',
    'grow/strain/hx/delete': 'grow/strain/strain/hx/delete.html',
    'grow/strain/hx/search': 'grow/strain/strain/hx/search.html',
    'grow/strain/strain': 'grow/strain/strain/detail.html',
    'grow/strain/strain/add_to_stock': 'grow/strain/strain/add_to_stock.html',
    'grow/strain/strain/add_to_stock2': 'grow/strain/strain/add_to_stock2.html',
    'grow/strain/strain/comment_create': 'grow/strain/strain/comment/create.html',
    'grow/strain/strain/comment_update': 'grow/strain/strain/comment/update.html',
    'grow/strain/strain/form': 'grow/strain/strain/form.html',
    'grow/strain/strain/hx/add_to_stock': 'grow/strain/strain/hx/add_to_stock.html',
    'grow/strain/strain/hx/add_to_stock2': 'grow/strain/strain/hx/add_to_stock2.html',
    'grow/strain/strain/hx/add_to_stock_dialog': 'grow/strain/strain/hx/dialog.html',
    'grow/strain/strain/hx/filter': 'grow/strain/strain/hx/filter.html',
    'grow/strain/strain/hx/growlogs': 'grow/strain/strain/hx/growlogs.html',
    'grow/strain/strain/hx/translation': 'grow/strain/strain/hx/translation.html',
    'grow/strain/strain/in_stock/hx/add': 'grow/strain/strain/hx/add_to_stock.html',
    'grow/strain/strain/in_stock/hx/remove': 'grow/strain/strain/hx/remove_from_stock.html',
    'grow/strain/strain/in_stock/hx/remove_invalid': 'grow/strain/strain/hx/remove_from_stock_invalid.html',
    'grow/strain/strain/in_stock/hx/notes': 'grow/strain/strain/hx/in_stock_notes.html',
    'grow/strain/strain/in_stock/hx/update': 'grow/strain/strain/hx/in_stock_update.html',

    'grow/strain/strain/image_upload': 'grow/strain/strain/image/upload.html',
    'grow/strain/strain/remove_from_stock': 'grow/strain/strain/remove_from_stock.html',
    'grow/strain/strain/remove_from_stock_invalid': 'grow/strain/strain/remove_from_stock_invalid.html',
    'grow/strain/strain_search_results': 'grow/strain/strain/search_results.html',
    'grow/strain/strain/translation': 'grow/strain/strain/translation.html',
    'grow/strain/strain/update': 'grow/strain/strain/update.html',
}

GROW_BUILTIN_BS_STRAIN_TEMPLATES = {
    # strain templates
    'grow/strain': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain'],
    'grow/strain/create': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/create'],
    'grow/strain/delete': GROW_BUILTIN_STRAIN_TEMPLATES['grow/strain/delete'],
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
    'grow/location/index': 'grow/location/index_bs.html',
    'grow/location/create': 'grow/location/create_bs.html',
    'grow/location/update': 'grow/location/update_bs.html',
    'grow/location/delete': 'grow/location/delete_bs.html',
    'grow/location/detail': 'grow/location/detail_bs.html',
    'grow/location/hx-type-change': 'grow/location/hx_locationtype_change_bs.html',
    'grow/location/hx-delete': 'grow/location/hx_delete_bs.html',
}

GROW_BUILTIN_BS_LOCATION_TEMPLATES = {
    # location templates
    'grow/location/index': GROW_BUILTIN_LOCATION_TEMPLATES['grow/location/index'],
    'grow/location/create': GROW_BUILTIN_LOCATION_TEMPLATES['grow/location/create'],
    'grow/location/update': GROW_BUILTIN_LOCATION_TEMPLATES['grow/location/update'],
    'grow/location/delete': GROW_BUILTIN_LOCATION_TEMPLATES['grow/location/delete'],
    'grow/location/detail': GROW_BUILTIN_LOCATION_TEMPLATES['grow/location/detail'],
    'grow/location/hx-type-change': GROW_BUILTIN_LOCATION_TEMPLATES['grow/location/hx-type-change'],
    'grow/location/hx-delete': GROW_BUILTIN_LOCATION_TEMPLATES['grow/location/hx-delete'],
}

GROW_BUILTIN_SIS_TEMPLATES = {
    'grow/seeds_in_stock': 'grow/seeds_in_stock/my_seeds_in_stock.html',
    'grow/seeds_in_stock/add': 'grow/seeds_in_stock/add.html',
    'grow/seeds_in_stock/remove': 'grow/seeds_in_stock/remove.html',
    'grow/seeds_in_stock/remove_invalid': 'grow/seeds_in_stock/remove_invalid.html',
    'grow/seeds_in_stock/hx/add': 'grow/seeds_in_stock/hx/add.html',
    'grow/seeds_in_stock/hx/remove': 'grow/seeds_in_stock/hx/remove.html',
    'grow/seeds_in_stock/hx/remove_invalid': 'grow/seeds_in_stock/hx/remove_invalid.html',
    'grow/seeds_in_stock/hx/info': 'grow/seeds_in_stock/hx/info.html',
    'grow/seeds_in_stock/hx/dialog': 'grow/seeds_in_stock/hx/dialog.html',
    'grow/seeds_in_stock/hx/info': 'grow/seeds_in_stock/hx/info.html',
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
    'grow/growlog/create': 'grow/growlog/growlog/create.html',
    'grow/growlog/delete': 'grow/growlog/growlog/delete.html',
    'grow/growlog/detail': 'grow/growlog/growlog/detail.html',
    'grow/growlog/update': 'grow/growlog/growlog/update.html',
    'grow/growlog/form': 'grow/growlog/growlog/form.html',

    'grow/growlog/entry/image_delete': 'grow/growlog/entry/image_delete.html',
    'grow/growlog/entry/image_upload': 'grow/growlog/entry/image_upload.html',
    'grow/growlog/entry/create': 'grow/growlog/entry/form.html',
    'grow/growlog/entry/update': 'grow/growlog/entry/form.html',
    'grow/growlog/entry/delete': 'grow/growlog/entry/delete.html',
    'grow/growlog/entry/form': 'grow/growlog/entry/form.html',
    'grow/growlog/entry/image/upload': 'grow/growlog/entry/image/upload.html',
    'grow/growlog/entry/image/delete': 'grow/growlog/entry/image/delete.html',
    'grow/growlog/entry/image/update': 'grow/growlog/entry/image/update.html',
    'grow/growlog/entry/image/hx/delete': 'grow/growlog/entry/image/hx/delete.html',
    'grow/growlog/entry/image/hx/upload': 'grow/growlog/entry/image/hx/upload.html',
    'grow/growlog/entry/image/hx/update': 'grow/growlog/entry/image/hx/update.html',
    'grow/growlog/entry/hx/delete': 'grow/growlog/entry/hx/delete.html',
    'grow/growlog/entry/hx/create': 'grow/growlog/entry/hx/form_dialog.html',
    'grow/growlog/entry/hx/update': 'grow/growlog/entry/hx/form_dialog.html',
    'grow/growlog/forbidden': 'grow/growlog/forbidden.html',
    'grow/growlog/hx/active_info' : 'grow/growlog/hx/active_info.html',
    'grow/growlog/hx/finished_info' : 'grow/growlog/hx/finished_info.html',
    'grow/growlog/hx/strains_grown': 'grow/growlog/hx/strains_grown.html',
    'grow/growlog/growlog/hx/entries': 'grow/growlog/growlog/hx/entries.html',
    'grow/growlog/growlog/hx/seeds_add': 'grow/growlog/growlog/hx/add_seeds.html',
    'grow/growlog/growlog/hx/description': 'grow/growlog/growlog/hx/description.html',
    'grow/growlog/growlog/hx/edit_notes': 'grow/growlog/growlog/hx/edit_notes.html',
    'grow/growlog/growlog/hx/notes': 'grow/growlog/growlog/hx/notes.html',
    'grow/growlog/growlog/hx/edit_description': 'grow/growlog/growlog/hx/edit_description.html',
    'grow/growlog/growlog/hx/strains':  'grow/growlog/growlog/hx/strains.html',
    'grow/growlog/growlog/hx/add_plants':  'grow/growlog/growlog/hx/add_plants.html',
    'grow/growlog/growlog/hx/remove_plants':  'grow/growlog/growlog/hx/remove_plants.html',
    'grow/growlog/growlog/hx/add_strain':  'grow/growlog/growlog/hx/add_strain.html',
    'grow/growlog/growlog/hx/delete_strain':  'grow/growlog/growlog/hx/delete_strain.html',
    'grow/growlog/my_growlogs': 'grow/growlog/my_growlogs.html',
    'grow/growlog/strains_grown': 'grow/growlog/strains_grown.html',
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
    'grow/user/hx-add_seeds_to_stock': 'grow/user/hx_add_seeds_to_stock.html',
    'grow/user/hx-remove_seeds_from_stock': 'grow/user/hx_remove_seeds_from_stock.html',
    'grow/user/info': 'grow/user/info.html',
}

GROW_BUILTIN_BS_USER_TEMPLATES = {
    'grow/user/hx-add_seeds_to_stock': GROW_BUILTIN_USER_TEMPLATES['grow/user/hx-add_seeds_to_stock'],
    'grow/user/hx-remove_seeds_from_stock': GROW_BUILTIN_USER_TEMPLATES['grow/user/hx-remove_seeds_from_stock'],
    'grow/user/info': GROW_BUILTIN_USER_TEMPLATES['grow/user/info'],
}

GROW_BUILTIN_UTILS_TEMPLATES = {
    'grow/utils/hx_select_date_days_sanitize': 'grow/utils/hx_select_date_days_sanitize.html',
}

GROW_BUILTIN_BS_UTILS_TEMPLATES = {
    'grow/utils/hx_select_date_days_sanitize': GROW_BUILTIN_UTILS_TEMPLATES['grow/utils/hx_select_date_days_sanitize'],
}

GROW_BUILTIN_TEMPLATES = {
    # home
    'grow/index': 'grow/index/index.html',


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
