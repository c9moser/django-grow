from django.urls import path

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
