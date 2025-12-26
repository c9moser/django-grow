from django.views import View
from django.http import (
    HttpRequest,
    HttpResponse,
)
from django.shortcuts import render
from .. import settings


class IndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, settings.BASE_TEMPLATE, {})
