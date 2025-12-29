from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic.edit import (
    CreateView,
    UpdateView,
)
from django.db.models.functions import Lower
from django.utils.safestring import mark_safe
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

from ._base import BaseView
from ..api.models import (
    Breeder,
    Strain
)
from .. import settings
from ..forms import StrainForm


class BreederIndexView(BaseView):
    template_name = settings.GROW_TEMPLATES['grow/strain']

    def get(self, request: HttpRequest) -> HttpResponse:
        breeders_allowed_to_edit = [breeder.id for breeder in Breeder.objects.all()]  # TODO: add logic
        allowed_to_create = True  # TODO: add logic
        breeders_id = []
        labels_id = []
        breeder_ids = []
        breeders = []

        breeder_id_format = "breeder-{}"
        for breeder in Breeder.objects.all().order_by(Lower("name")):
            breeders.append(breeder)
            if breeder.name[0].isdigit():
                if 'breeder-num' in breeder_ids:
                    breeders_id.append((breeder, None))
                else:
                    breeder_ids.append('breeder-num')
                    breeders_id.append((breeder, 'breeder-num'))
                    labels_id.append('breeder-num', '0-9')
            else:
                id = breeder_id_format.format(breeder.name[0].lower())
                if id in breeder_ids:
                    breeders_id.append((breeder, None, None))
                else:
                    breeder_ids.append(id)
                    labels_id.append((breeder.name[0].upper(), id))
                    breeders_id.append((breeder, id))

        if settings.USE_BOOTSTRAP:
            label_format = "<a class=\"link-body-emphasis link-opacity-50 link-opacity-100-hover link-underline-opacity-50 link-underline-opacity-75-hover\" href=\"#{id}\">{label}</a>"  # noqa: E501
        else:
            label_format = "<a href=\"#{id}\">{label}</a>"
        labels = ', '.join(label_format.format(id=id, label=label) for label, id in labels_id)
        labels = mark_safe(labels)
        return render(request, self.template_name, context={
            'breeder_count': Breeder.objects.count(),
            'breeders': breeders,
            'breeders_id': breeders_id,
            'labels': labels,
            'breeders_allowed_to_edit': breeders_allowed_to_edit,
            'allowed_to_create': allowed_to_create
        })


class BreederView(BaseView):
    template_name = settings.GROW_TEMPLATES['grow/strain/breeder']

    def get(self, request: HttpRequest, slug: str) -> HttpResponse:
        breeder = get_object_or_404(Breeder, slug=slug)
        can_add_strains = True  # TODO: add logic
        strains_allowed_to_edit = [strain.id for strain in breeder.strains.all()]  # TODO: add logic
        strains = breeder.strains.all().order_by('name')
        return render(request, self.template_name, context={
            'breeder': breeder,
            'can_add_strains': can_add_strains,
            'strains': strains,
            'strains_allowed_to_edit': strains_allowed_to_edit,
        })


class BreederCreateView(CreateView):
    template_name = settings.GROW_TEMPLATES['grow/strain/breeder/create']
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
        self._slug = form.cleaned_data['slug']
        return super().form_valid(form)

    @property
    def success_url(self):
        return reverse("grow:breeder-detail", kwargs={'slug': self._slug})


class BreederUpdateView(UpdateView):
    template_name = settings.GROW_TEMPLATES["grow/strain/breeder/update"]
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


class StrainView(BaseView):
    template_name = settings.GROW_TEMPLATES["grow/strain/detail"]

    def get(self, request: HttpRequest, breeder_slug: str, slug: str) -> HttpResponse:
        breeder = get_object_or_404(Breeder, slug=breeder_slug)
        strain = get_object_or_404(breeder.strains, slug=slug)
        return render(request, self.template_name, context={
            'strain': strain,
        })


class StrainCreateView(LoginRequiredMixin, View):
    template_name = settings.GROW_TEMPLATES["grow/strain/create"]

    def get(self, request: HttpRequest, breeder_slug: str) -> HttpResponse:
        breeder = get_object_or_404(Breeder, slug=breeder_slug)

        return render(request, self.template_name, context={
            'breeder': breeder,
            'form': StrainForm(),
        })

    def post(self, request: HttpRequest, breeder_slug: str) -> HttpResponse:
        breeder = get_object_or_404(Breeder, slug=breeder_slug)
        form = StrainForm(request.POST)

        if form.is_valid():
            strain = form.save(commit=False)
            strain.breeder = breeder
            strain.save()

            return redirect("grow:strain-detail",kwargs={
                'breeder_slug': breeder.slug,
                'slug': strain.slug,
            })

        form.fields['name'] = strain.name

        return render(request, self.template_name, context={
            'breeder': breeder,
            'form': form,
        })


class StrainUpdateView(BaseView):
    template_name = "grow/strain/strain_update.html"

    def get(self, request: HttpRequest, breeder_slug: str, slug: str) -> HttpResponse:
        strain = Strain.objects.get(breeder__slug=breeder_slug, slug=slug)
        return render(request, self.template_name, context={
            'breeder': strain.breeder,
            'form': StrainForm(instance=strain)
        })

    def post(self, request: HttpRequest, breeder_slug: str, slug: str) -> HttpResponse:
        breeder = get_object_or_404(Breeder, slug=breeder_slug)
        strain = get_object_or_404(breeder.strains, slug=slug)

        form = StrainForm(request.POST, instance=strain)

        if form.is_valid():
            strain = form.save(commit=False)
            strain.save()

            return redirect(reverse("grow:strain-detail", kwargs={
                'breeder_slug': breeder.slug,
                'slug': strain.slug,
            }))

        form.fields['name'] = strain.name

        return render(request, self.template_name, context={
            'breeder': breeder,
            'form': form,
        })
