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
