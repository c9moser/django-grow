
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.views import View
# from django.views.generic import FormView
from django.shortcuts import render
from django.utils.translation import gettext as _
from grow.views._base import BaseView

from ..models import User
from ..forms import (
    UserAccountForm,
    UserPasswordForm,
)


class PublicUserProfileView(BaseView):
    pass


class ProfileView(LoginRequiredMixin, View):
    pass


class ProfileEditView(LoginRequiredMixin, View):
    template_name = "core/user/profile_update.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name, context={})


class HxAccountView(LoginRequiredMixin, View):
    template_name = "core/user/hx_account.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name, context={
            'form': UserAccountForm(instance=request.user),
        })

    def post(self, request: HttpRequest) -> HttpResponse:
        form = UserAccountForm(request.POST, instance=request.user)

        username_error = None
        username_valid = False
        email_error = None
        email_valid = False
        first_name_valid = False
        last_name_valid = False

        if form.is_valid():

            if 'username' in form.changed_data:
                try:
                    user_to_check = User.objects.get(
                        username=form.cleaned_data['username']
                    )
                    if user_to_check.pk != self.request.user.pk:
                        username_error = _("Username is already taken!")
                    else:
                        username_valid = True
                except User.DoesNotExist:
                    username_valid = True

            if 'email' in form.changed_data:
                try:
                    user_to_check = User.objects.get(
                        email=form.cleaned_data['email']
                    )
                    if user_to_check.pk != self.request.user.pk:
                        email_error = _("Email is already taken!")
                    else:
                        email_valid = True
                except User.DoesNotExist:
                    email_valid = True

            if 'first_name' in form.changed_data:
                first_name_valid = True
            if 'last_name' in form.changed_data:
                last_name_valid = True

            form.save(commit=True)
        else:
            pass

        return render(request, self.template_name, context={
            'username_error': username_error,
            'username_valid': username_valid,
            'email_error': email_error,
            'email_valid': email_valid,
            'last_name_valid': last_name_valid,
            'first_name_valid': first_name_valid,
            'form': form,
        })


class HxPasswordView(LoginRequiredMixin, View):
    template_name = "core/user/hx_password.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name, context={
            'form': UserPasswordForm()
        })
