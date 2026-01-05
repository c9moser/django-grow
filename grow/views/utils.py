from ._base import BaseView
from .. import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


class HxSelectDateDaysSanitizeView(BaseView):
    template_name = settings.GROW_TEMPLATES['grow/utils/hx_select_date_days_sanitize']

    def get(self, request: HttpRequest, year: int, month: int) -> HttpResponse:
        if month < 1:
            month = 1
        elif month > 12:
            month = 12

        if year % 4 == 0:
            if year % 100 == 0:
                if year % 400 == 0:
                    leap_year = True
                else:
                    leap_year = False
            else:
                leap_year = True
        else:
            leap_year = False

        month_days = [31, 29 if leap_year else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        max_day = month_days[month - 1]

        return render(request, self.template_name, context={
            'days': range(1, max_day + 1),
        })
