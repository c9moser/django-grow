from django.views import View
from .. import settings

if settings.LOGIN_REQUIRED:
    from django.contrib.auth.mixins import LoginRequiredMixin

    class BaseView(LoginRequiredMixin, View):
        pass

else:
    class BaseView(View):
        pass
