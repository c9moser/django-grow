from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
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
from ..forms import (
    DeleteWithSlugForm,
    StrainForm
)

from ..api.permission import growlog_user_is_allowed_to_view


class BreederIndexView(BaseView):
    template_name = settings.GROW_TEMPLATES['grow/strain']

    def get(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            breeders_allowed_to_edit = [
                breeder.id for breeder in Breeder.objects.all()
            ]  # TODO: add logic
            breeders_allowed_to_delete = [
                breeder.id for breeder in Breeder.objects.all()
                if breeder.growlog_count == 0
            ]
            allowed_to_add_breeder = True  # TODO: add logic
        else:
            breeders_allowed_to_edit = []
            breeders_allowed_to_delete = []
            allowed_to_add_breeder = False

        breeders_id = []
        labels_id = []
        breeder_ids = []
        breeders = []

        breeder_id_format = "breeder-{}"
        for breeder in Breeder.objects.all().order_by(Lower("name")):
            breeders.append(breeder)
            if breeder.name[0].isdigit():
                if 'breeder-num' in breeder_ids:
                    breeders_id.append((breeder, None, None))
                else:
                    breeder_ids.append('breeder-num')
                    breeders_id.append((breeder, 'breeder-num', '0-9'))
                    labels_id.append('breeder-num', '0-9')
            else:
                id = breeder_id_format.format(breeder.name[0].lower())
                if id in breeder_ids:
                    breeders_id.append((breeder, None, None))
                else:
                    breeder_ids.append(id)
                    labels_id.append((breeder.name[0].upper(), id))
                    breeders_id.append((breeder, id, breeder.name[0].upper()))

        group_breeders = (Breeder.objects.all().count() > 30)

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
            'breeders_allowed_to_delete': breeders_allowed_to_delete,
            'allowed_to_add_breeder': allowed_to_add_breeder,
            'group_breeders': group_breeders,
        })


class BreederView(BaseView):
    template_name = settings.GROW_TEMPLATES['grow/breeder/detail']

    def get(self, request: HttpRequest, slug: str) -> HttpResponse:
        breeder = get_object_or_404(Breeder, slug=slug)
        allowed_to_edit = request.user.is_authenticated  # TODO: add logic
        allowed_to_delete = request.user.is_authenticated  # TODO: allowed_to_delete
        allowed_to_add_strains = request.user.is_authenticated  # TODO: add logic

        if request.user.is_authenticated:
            strains_allowed_to_edit = [
                strain.id for strain in breeder.strains.all()
            ]  # TODO: add logic
        else:
            strains_allowed_to_edit = []

        strains = breeder.strains.all().order_by('name')
        return render(request, self.template_name, context={
            'breeder': breeder,
            'allowed_to_edit': allowed_to_edit,
            'allowed_to_delete': allowed_to_delete,
            'allowed_to_add_strains': allowed_to_add_strains,
            'strains': strains,
            'strains_allowed_to_edit': strains_allowed_to_edit,
        })


class BreederCreateView(LoginRequiredMixin, CreateView):
    template_name = settings.GROW_TEMPLATES['grow/breeder/create']
    model = Breeder
    fields = [
        "slug",
        "name",
        "description",
        "description_type_data",
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


class BreederUpdateView(LoginRequiredMixin, UpdateView):
    template_name = settings.GROW_TEMPLATES["grow/breeder/update"]
    model = Breeder

    fields = [
        "slug",
        "name",
        "description",
        "description_type_data",
        "breeder_url",
        "seedfinder_url",
        "logo_url",
        "logo_image",
    ]

    def form_valid(self, form):
        ret = super().form_valid(form)
        self._slug = form.cleaned_data['slug']
        return ret

    @property
    def success_url(self):
        return reverse("grow:breeder-detail", kwargs={'slug': self.get_object().slug})


class BreederDeleteView(LoginRequiredMixin, View):
    template_name = settings.GROW_TEMPLATES['grow/breeder/delete']
    form_class = DeleteWithSlugForm
    success_url = reverse_lazy("grow:breeder-overview")

    def get(self, request: HttpRequest, slug: str) -> HttpResponse:
        breeder = get_object_or_404(Breeder, slug=slug)
        return render(request, self.template_name, context={
            'form': self.form_class(),
            'breeder': breeder,
        })

    def post(self, request: HttpRequest, slug: str) -> HttpResponse:
        breeder = get_object_or_404(Breeder, slug=slug)
        form = self.form_class(request.POST)
        delete_error = None

        if form.is_valid():
            if form.cleaned_data['slug'] == breeder.slug:
                try:
                    breeder.delete()
                    return redirect(self.success_url)

                except Exception as error:
                    delete_error = str(error)

        return render(request, self.template_name, context={
            'form': self.form_class(),
            'delete_error': delete_error,
            'breeder': breeder,
        })


class HxBreederDelete(LoginRequiredMixin, View):
    pass


class StrainView(BaseView):
    template_name = settings.GROW_TEMPLATES["grow/strain/detail"]

    def get(self, request: HttpRequest, breeder_slug: str, slug: str) -> HttpResponse:
        breeder = get_object_or_404(Breeder, slug=breeder_slug)
        strain = get_object_or_404(breeder.strains, slug=slug)
        growlogs = [
            growlog_strain.growlog
            for growlog_strain in strain.growlog_strains.all().order_by(Lower('growlog__name'))
            if growlog_user_is_allowed_to_view(self.request.user, growlog_strain.growlog)
        ]
        allowed_to_edit = request.user.is_authenticated
        allowed_to_delete = request.user.is_authenticated and strain.growlog_count == 0

        return render(request, self.template_name, context={
            'strain': strain,
            'growlogs': growlogs,
            'allowed_to_delete': allowed_to_delete,
            'allowed_to_edit': allowed_to_edit,
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
            if form.cleaned_data['flowering_time_unit'] == 'w':
                form.cleaned_data['flowering_time_days'] = (
                    form.cleaned_data['flowering_time_days'] * 7
                )
            strain = form.save(commit=False)
            strain.breeder = breeder
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


class StrainUpdateView(LoginRequiredMixin, View):
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
            if form.cleaned_data['flowering_time_unit'] == 'w':
                strain.flowering_time_days = strain.flowering_time_days * 7
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
