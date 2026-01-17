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


urlpatterns = [
    path('api/', include('grow.growapi.urls')),
    *i18n_patterns(
        path('accounts/', include('allauth.urls')),
        path('', include('grow.urls')),
        path('', include('core.urls'))),
]
if settings.ADMIN_URL:
    urlpatterns.insert(0, path(settings.ADMIN_URL, admin.site.urls))

if settings.INCLUDE_WIKI:
    urlpatterns.insert(-1, path('wiki/', include('tinywiki.urls')))

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns.insert(0, path('__reload__/', include('django_browser_reload.urls')))
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.autodiscover()
admin.site.site_header = "Grow Administration"
admin.site.site_title = "Grow Admin"
admin.site.index_title = "Grow Admin Portal"
admin.site.login = secure_admin_login(admin.site.login)