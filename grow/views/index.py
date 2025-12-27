from django.http import (
    HttpRequest,
    HttpResponse,
)
from django.shortcuts import render

from ._base import BaseView
from ..api.models import Growlog, Strain
from ..api.enums import PermissionType as Permission


class IndexView(BaseView):
    template_name = "grow/index/index.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            user_growlogs = Growlog.objects.filter(
                grower=self.request.user,
                finished_at__isnull=True)
            new_growlogs = []
            for growlog in Growlog.objects.exclude(grower=request.user).order_by("started_at"):
                if growlog.is_user_allowed_to_view(request.user):
                    new_growlogs.append(growlog)
                if len(new_growlogs) >= 10:
                    break
        else:
            user_growlogs = None
            new_growlogs = Growlog.objects.filter(
                permission_data=Permission.PUBLIC.value).order_by(
                    'started_at')[:10]

        new_strains = Strain.objects.all().order_by('-added_at')[:20]

        return render(request, self.template_name, {
            'user_growlogs': user_growlogs,
            'new_growlogs': new_growlogs,
            'new_strains': new_strains
        })
