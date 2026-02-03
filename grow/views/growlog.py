from django.shortcuts import get_object_or_404, render
from django.http import HttpRequest, HttpResponse
# from django.urls import reverse

from ..growapi.models import Growlog, GrowlogEntry
from ._base import BaseView


class GrowlogView(BaseView):
    def get(self, request: HttpRequest, key: str) -> HttpResponse:
        growlog = get_object_or_404(Growlog, key=key, owner=request.user)
        entries = GrowlogEntry.objects.filter(growlog=growlog).order_by('-timestamp')
        context = {
            'growlog': growlog,
            'entries': entries,
        }
        return render(request, 'growlog/detail.html', context)
