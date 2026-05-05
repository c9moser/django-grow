"""
URL configuration for django_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.conf import settings
from django.contrib import admin
from allauth.account.decorators import secure_admin_login
from django.conf.urls.i18n import i18n_patterns


locale_patterns = [
        path('accounts/', include('allauth.urls')),
        path('invitations/', include('invitations.urls', namespace='invitations')),
        path('', include('grow.urls')),
        path('', include('core.urls')),
]

urlpatterns = []

if settings.REST_FRAMEWORK_ENABLED:
    import grow.growapi.urls
    from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
    locale_patterns += [
        path('api/grow/', include(grow.growapi.urls)),
    ]
    if settings.BROWSABLE_REST_FRAMEWORK:
        locale_patterns += [
            path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
            path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        ]

if settings.ADMIN_URL:
    urlpatterns.insert(0, path(settings.ADMIN_URL, admin.site.urls))
else:
    urlpatterns.insert(0, path('admin/', admin.site.urls))

if settings.INCLUDE_WIKI:
    locale_patterns.append(path('wiki/', include('tinywiki.urls')))

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns.insert(0, path('__reload__/', include('django_browser_reload.urls')))
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(*locale_patterns)

admin.autodiscover()
admin.site.site_header = "Grow Administration"
admin.site.site_title = "Grow Admin"
admin.site.index_title = "Grow Admin Portal"
admin.site.login = secure_admin_login(admin.site.login)