from django.urls import path

from .views.user import (
    ProfileView,
    ProfileEditView,
    PublicUserProfileView,

    HxAccountView,
    HxPasswordView,
)

from django.conf.urls.i18n import i18n_patterns
app_name = "core"
urlpatterns = i18n_patterns(
    path("me/", ProfileView.as_view(), name="user"),
    path("me/edit/", ProfileEditView.as_view(), name="account"),
    path("profile/<int:pk>", PublicUserProfileView.as_view(), name="public_profile"),
    path("__hx__/account/", HxAccountView.as_view(), name="hx_account"),
    path("__hx__/password/", HxPasswordView.as_view(), name="hx_password"),
)
