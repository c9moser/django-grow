from django.urls import path

from core import settings

from .views.user import (
    ProfileView,
    ProfileEditView,
    PublicUserProfileView,

    HxAccountView,
    HxPasswordView,
)

app_name = "core"

urlpatterns = [
    path("me/", ProfileView.as_view(), name="user"),
    path("me/edit/", ProfileEditView.as_view(), name="account"),
    path("profile/<int:pk>", PublicUserProfileView.as_view(), name="public_profile"),
    path("__hx__/account/", HxAccountView.as_view(), name="hx_account"),
    path("__hx__/password/", HxPasswordView.as_view(), name="hx_password"),
]

if settings.APACHE_AUTH_ENABLED:
    from .views.apache import ApacheLoginView
    a2login_url = settings.APACHE_AUTH_LOGIN_URL.lstrip('/')
    urlpatterns += [
        path(a2login_url, ApacheLoginView.as_view(), name="a2login"),
    ]
