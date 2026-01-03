from django.http import (
    HttpRequest,
    HttpResponse,
)
from django.shortcuts import render

from ._base import BaseView
from ..growapi.models import Growlog, Strain
from ..growapi.enums import PermissionType as Permission
from .. import settings


class IndexView(BaseView):
    template_name = settings.GROW_TEMPLATES['grow/index']

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

        new_strains = Strain.objects.all().order_by('-added_at')[:10]

        return render(request, self.template_name, {
            'user_growlogs': user_growlogs,
            'new_growlogs': new_growlogs,
            'new_strains': new_strains
        })


class HxSanitizeDateDayView(BaseView):
    template_name = settings.GROW_TEMPLATES['grow/index/sanitize-date-day']

    def get(self, request: HttpRequest, year: int, month: int) -> HttpResponse:
        if month < 1:
            month = 1
        elif month > 12:
            month = 12

        if year < 1900:
            year = 1900
        elif year > 2100:
            year = 2100

        months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if year % 4 == 0:
            if year % 100 == 0:
                if year % 400 == 0:
                    months[1] = 29
            else:
                months[1] = 29

        days = months[month - 1]
        print(days)
        return render(request, self.template_name, context={
            'days': list(range(1, days + 1))
        })
