from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic.edit import (
    CreateView,
    UpdateView,
)
from django.db.models.functions import Lower

from ._base import BaseView
from ..api.models import (
    Breeder,
    Strain
)


class BreederIndexView(BaseView):
    template_name = "grow/strain/index.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        breeders_allowed_to_edit = [breeder.id for breeder in Breeder.objects.all()]
        breeders_id_label = []
        breeder_ids = []
        breeders = []

        breeder_id_format = "breeder-{}"
        for breeder in Breeder.objects.all().order_by(Lower("name")):
            breeders.append(breeder)
            if breeder.name[0].isdigit():
                if 'breeder-num' in breeder_ids:
                    breeders_id_label.append((breeder, None, None))
                else:
                    breeders_id_label.append((breeder, 'breeder-num', '0-9'))
            else:
                id = breeder_id_format.format(breeder.name[0].lower())
                if id in breeder_ids:
                    breeders_id_label.append((breeder, None, None))
                else:
                    breeder_ids.append(id)
                    breeders_id_label.append((breeder, id, breeder.name[0].upper()))

        return render(request, self.template_name, context={
            'breeder_count': Breeder.objects.count(),
            'breeders': breeders,
            'breederd_id_label': breeders_id_label,
            'breeders_allowed_to_edit': breeders_allowed_to_edit,
        })


class BreederView(BaseView):
    template_name = "grow/strain/breeder.html"

    def get(self, request: HttpRequest, key: str) -> HttpResponse:
        breeder = get_object_or_404(Breeder, key=key)

        return render(request, self.template_name, context={
            'breeder': breeder,
        })


class BreederCreateView(CreateView):
    template_name = "grow/strain/breeder_create.html"
    model = Breeder
    fields = [
        "slug",
        "name",
        "description",
        "description_type",
        "breeder_url",
        "seedfinder_url",
        "logo_url",
        "logo_image",
    ]

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        self._key = form.cleaned_data['key']
        return super().form_valid(form)

    @property
    def success_url(self):
        return reverse("grow:breeder-detail", kwargs={'key': self._key})


class BreederUpdateView(UpdateView):
    template_name = "grow/strain/breeder_update.html"
    model = Breeder

    fields = [
        "slug",
        "name",
        "description",
        "description_type",
        "breeder_url",
        "seedfinder_url",
        "logo_url",
        "logo_image",
    ]

    def form_valid(self, form):
        ret = super().form_valid(form)
        self._key = form.cleaned_data['key']
        return ret

    @property
    def success_url(self):
        return reverse("grow:breeder-detail", kwargs={'key': self._key})