from django.http import (
    HttpRequest,
    HttpResponse,
)
from django.shortcuts import render

from ._base import BaseView
from ..growapi.models import Growlog, Strain
# from ..growapi.enums import PermissionType as Permission
from ..growapi.permission import growlog_user_is_allowed_to_view
from .. import settings


class IndexView(BaseView):
    template_name = settings.GROW_TEMPLATES['grow/index']

    def get(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            user_growlogs = Growlog.objects.filter(
                grower=self.request.user,
                finished_at__isnull=True)
            new_growlogs = []
            for growlog in Growlog.objects.all().order_by("-started_at"):
                if growlog_user_is_allowed_to_view(request.user, growlog):
                    new_growlogs.append(growlog)
                if len(new_growlogs) >= 10:
                    break
        else:
            user_growlogs = None
            new_growlogs = []
            for growlog in Growlog.objects.all().order_by('-started_at'):
                if growlog_user_is_allowed_to_view(request.user, growlog):
                    new_growlogs.append(growlog)
                if len(new_growlogs) >= 10:
                    break

        new_strains = Strain.objects.all().order_by('-added_at')[:10]

        return render(request, self.template_name, {
            'user_growlogs': user_growlogs,
            'new_growlogs': new_growlogs,
            'new_strains': new_strains
        })
