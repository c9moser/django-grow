from django.views import View
from django.http import (
    HttpRequest,
    HttpResponse,
)
from django.shortcuts import render

from .. import settings
from ._base import BaseView


class IndexView(BaseView):
    template_name = "grow/index/index.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name, {})
