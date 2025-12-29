from django import forms

from django.utils.translation import gettext_lazy as _
from ..models import User


class UserAccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
        ]


class UserPasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(),
        max_length=255,
        label=_("Password")
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(),
        max_length=255,
        label=_("New password")
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(),
        max_length=255,
        label=_("Confirm your password")
    )
