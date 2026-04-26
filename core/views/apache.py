from django.views import View
from django.shortcuts import render
from core.settings import (
    APACHE_AUTH_ENABLED,
    APACHE_AUTH_LOGIN_ACTION_URL
)


if APACHE_AUTH_ENABLED:
    class ApacheLoginView(View):
        def get(self, request):
            if request.user.is_authenticated:
                username = request.user.username
            else:
                username = ''

            action = request.GET.get('action', APACHE_AUTH_LOGIN_ACTION_URL)

            return render(request, 'core/a2login.html', {
                'username': username,
                'action': action
            })
