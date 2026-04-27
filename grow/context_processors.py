from typing import Any
from django.http import HttpRequest
from . import settings


def grow(request: HttpRequest) -> dict[str, Any]:
    from .growapi.models.user import GrowUserSettings
    """
    grow contexts
    """

    paginate = settings.GROW_PAGINATE
    growlog_paginate = settings.GROW_GROWLOG_PAGINATE

    if request.user.is_authenticated:
        try:
            user_settings = request.user.grow_settings
        except GrowUserSettings.DoesNotExist or GrowUserSettings.RelatedObjectDoesNotExist:

            user_settings = GrowUserSettings.objects.create(user=request.user,
                                                            paginate=paginate,
                                                            growlog_paginate=growlog_paginate)
        paginate = user_settings.paginate
        growlog_paginate = user_settings.growlog_paginate

    if 'paginate' in request.GET:
        try:
            paginate = int(request.GET['paginate'])
            growlog_paginate = paginate
        except ValueError:
            pass

    if 'grow_paginate' in request.GET:
        try:
            paginate = int(request.GET['grow_paginate'])
        except ValueError:
            pass

    if 'growlog_paginate' in request.GET:
        try:
            growlog_paginate = int(request.GET['growlog_paginate'])
        except ValueError:
            pass

    httpd_auth_method = request.GET.get('httpd_auth_method', None)
    httpd_login = (httpd_auth_method == 'login')
    httpd_logout = (httpd_auth_method == 'logout')

    return {
        'base_template': settings.BASE_TEMPLATE,
        'use_bootstrap': settings.USE_BOOTSTRAP,
        'grow_site_title': settings.GROW_SITE_TITLE,
        'site_title': settings.GROW_SITE_TITLE,
        'grow_head_title': settings.GROW_HEAD_TITLE,
        'GROW_IS_MAIN_APP': settings.GROW_IS_MAIN_APP,
        'grow_paginate': paginate,
        'growlog_paginate': growlog_paginate,
        'DEBUG': settings.settings.DEBUG,
        'allow_signup': settings.ALLOW_SIGNUP,
        'APACHE_AUTH_ENABLED': settings.APACHE_AUTH_ENABLED,
        'APACHE_AUTH_TYPE': settings.APACHE_AUTH_TYPE,
        'APACHE_AUTH_LOGIN_URL': settings.APACHE_AUTH_LOGIN_URL,
        'APACHE_AUTH_LOGIN_ACTION_URL': settings.APACHE_AUTH_LOGIN_ACTION_URL,
        'APACHE_AUTH_LOGIN_METHOD': settings.APACHE_AUTH_LOGIN_METHOD,
        'perform_httpd_login': httpd_login,
        'perform_httpd_logout': httpd_logout,
    }
