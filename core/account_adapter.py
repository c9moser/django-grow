from django.http import HttpRequest
from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter


class AccountAdapter(DefaultAccountAdapter):

    @property
    def settings_allow_signup(self):
        return getattr(settings, 'ALLOW_SIGNUP', True)

    def is_open_for_signup(self, request: HttpRequest):
        """
        Checks thether or not the site is open for singups.

        Next to simply returning True/False you can also intervene the
        regular flow by raising an ImmediateHttpResponse

        (Comment reproduced from the overridden method.)

        :param request: The request for account creations
        :type request: HttpRequest
        """
        return self.settings_allow_signup

    def get_login_redirect_url(self, request: HttpRequest):
        url = super().get_login_redirect_url(request)
        if settings.APACHE_AUTH_ENABLED:
            url += '?httpd_auth_method=login'
        return url

    def get_logout_redirect_url(self, request: HttpRequest):
        url = super().get_logout_redirect_url(request)
        if settings.APACHE_AUTH_ENABLED:
            url += '?httpd_auth_method=logout'
        return url
