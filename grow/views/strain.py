from datetime import date
import re

from django.conf import settings as django_settings
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.translation import get_language, activate
from django.views.generic.edit import (
    CreateView,
    UpdateView,
)
from django.db.models import Count
from django.db.models.functions import Lower
from django.utils.safestring import mark_safe
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import FormView


from grow.growapi.models.strain import StrainUserComment

from ._base import BaseView

from ..growapi.models import (
    Breeder,
    Strain,
    StrainsInStock,
)
from .. import settings

from ..forms import (
    BreederFilterForm,
    BreederTranslationForm,
    DeleteWithSlugForm,
    StrainForm,
    StrainImageUploadForm,
    StrainAddToStockForm,
    StrainAddToStock2Form,
    StrainRemoveFromStockForm,
    StrainSearchForm,
    StrainFilterForm,
    StrainTranslationForm,
    StrainCommentForm,
)

from ..growapi.permission import growlog_user_is_allowed_to_view


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

        group_breeders = (len(breeder_ids) > 3)

        if settings.USE_BOOTSTRAP:
            label_format = "<a class=\"link-body-emphasis link-opacity-50 link-opacity-100-hover link-underline-opacity-50 link-underline-opacity-75-hover\" href=\"#{id}\">{label}</a>"  # noqa: E501
        else:
            label_format = "<a href=\"#{id}\">{label}</a>"
        labels = ', '.join(label_format.format(id=id, label=label) for label, id in labels_id)
        labels = mark_safe(labels)

        return render(request, self.template_name, context={
            'breeder_filter_form': BreederFilterForm(),
            'strain_search_form': StrainSearchForm(),
            'breeder_count': Breeder.objects.count(),
            'strain_count': Strain.objects.count(),
            'breeders': breeders,
            'breeders_id': breeders_id,
            'labels': labels,
            'breeders_allowed_to_edit': breeders_allowed_to_edit,
            'breeders_allowed_to_delete': breeders_allowed_to_delete,
            'allowed_to_add_breeder': allowed_to_add_breeder,
            'group_breeders': group_breeders,
        })


class HxBreederFilterView(BaseView):
    template_name = settings.GROW_TEMPLATES['grow/breeder/hx/filter']

    def post(self, request: HttpRequest) -> HttpResponse:
        form = BreederFilterForm(request.POST)
        if form.is_valid():
            search_query = form.cleaned_data['search_query']
        else:
            search_query = None

        if search_query:
            breeders = Breeder.objects.filter(name__icontains=search_query).order_by(Lower("name"))
        else:
            breeders = Breeder.objects.all().order_by(Lower("name"))

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

        breeder_id_format = "breeder-{}"
        for breeder in breeders:
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

        group_breeders = (breeders.count() > 30)

        if settings.USE_BOOTSTRAP:
            label_format = "<a class=\"link-body-emphasis link-opacity-50 link-opacity-100-hover link-underline-opacity-50 link-underline-opacity-75-hover\" href=\"#{id}\">{label}</a>"  # noqa: E501
        else:
            label_format = "<a href=\"#{id}\">{label}</a>"
        labels = ', '.join(label_format.format(id=id, label=label) for label, id in labels_id)
        labels = mark_safe(labels)

        return render(request, self.template_name, context={
            'breeder_count': breeders.count(),
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

        language_code = get_language()

        if 'language_code' in request.GET:
            language_code = request.GET['language_code']
        elif 'lang_code' in request.GET:
            language_code = request.GET['lang_code']
        elif 'lang' in request.GET:
            language_code = request.GET['lang']

        if language_code == 'en':
            language_code = 'en-us'

        supported_languages = [
            i[0] for i in getattr(
                django_settings,
                'LANGUAGES',
                [
                    ('en-us',),
                    ('de',)
                ])
        ]

        if language_code in supported_languages:
            activate(language_code)

        translation = breeder.get_translation(language_code)

        allowed_to_edit = request.user.is_authenticated  # TODO: add logic
        allowed_to_delete = request.user.is_authenticated  # TODO: allowed_to_delete
        allowed_to_add_strains = request.user.is_authenticated  # TODO: add logic

        if request.user.is_authenticated:
            strains_allowed_to_edit = [
                strain.id for strain in breeder.strains.all()
            ]  # TODO: add logic
        else:
            strains_allowed_to_edit = []

        if request.user.is_authenticated:
            strains_allowed_to_delete = [
                strain.id for strain in breeder.strains.all()
                if strain.growlog_count == 0
            ]
        else:
            strains_allowed_to_delete = []

        allowed_to_translate = request.user.is_authenticated  # TODO: add logic
        strains = breeder.strains.all().order_by('name')
        return render(request, self.template_name, context={
            'breeder': breeder,
            'allowed_to_edit': allowed_to_edit,
            'allowed_to_delete': allowed_to_delete,
            'allowed_to_add_strains': allowed_to_add_strains,
            'strains': strains,
            'strains_allowed_to_edit': strains_allowed_to_edit,
            'strains_allowed_to_delete': strains_allowed_to_delete,
            'filter_strains_form': StrainFilterForm(),
            'allowed_to_translate': allowed_to_translate,
            'breeder_translation': translation,
            'breeder_url': (translation.breeder_url
                            if translation and translation.breeder_url
                            else breeder.breeder_url),
            'seedfinder_url': (translation.seedfinder_url
                               if translation and translation.seedfinder_url
                               else breeder.seedfinder_url),
            'breeder_description_html': (translation.description_html
                                         if translation and translation.description
                                         else breeder.description_html),
            'translation': translation,
        })


class HxStrainFilterView(BaseView):
    template_name = settings.GROW_TEMPLATES['grow/strain/strain/hx/filter']

    def post(self, request: HttpRequest, breeder_pk: int) -> HttpResponse:
        form = StrainFilterForm(request.POST)
        if form.is_valid():
            search_query = form.cleaned_data['search_query']
        else:
            search_query = None

        breeder = get_object_or_404(Breeder, pk=breeder_pk)

        if search_query:
            strains = breeder.strains.filter(name__icontains=search_query).order_by(Lower("name"))
        else:
            strains = breeder.strains.all().order_by(Lower("name"))

        if request.user.is_authenticated:
            # TODO: add logic
            strains_allowed_to_edit = [strain.id for strain in strains]
            # TODO: add logic
            strains_allowed_to_delete = [strain.id for strain in strains if strain.growlog_count == 0]  # noqa: E501
            allowed_to_add_strains = True  # TODO: add logic
            allowed_to_translate = True  # TODO: add logic
        else:
            strains_allowed_to_edit = []
            strains_allowed_to_delete = []
            allowed_to_add_strains = False

        return render(request, self.template_name, context={
            'breeder': breeder,
            'strains': strains,
            'strains_allowed_to_edit': strains_allowed_to_edit,
            'strains_allowed_to_delete': strains_allowed_to_delete,
            'allowed_to_add_strains': allowed_to_add_strains,
            'allowed_to_translate': allowed_to_translate,
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
        breeder = form.save(commit=False)
        breeder.created_by = self.request.user
        breeder.save()

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


class HxBreederDeleteView(LoginRequiredMixin, FormView):
    template_name = settings.GROW_TEMPLATES['grow/breeder/hx/delete']
    form_class = DeleteWithSlugForm
    success_url = reverse_lazy("grow:breeder-overview")

    def get_failed_url(self) -> str:
        return reverse("grow:breeder-detail", kwargs={'slug': self.breeder.slug})

    def get_context_data(self, **kwargs):
        context = super(HxBreederDeleteView, self).get_context_data(**kwargs)
        context['breeder'] = self.breeder
        context['form'] = self.form_class()
        if self.form_error:
            context['form_error'] = self.form_error
        return context

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.form_error = None
        self.breeder = get_object_or_404(Breeder, pk=pk)
        return super(HxBreederDeleteView, self).get(request)

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.form_error = None
        self.breeder = get_object_or_404(Breeder, pk=pk)
        return super(HxBreederDeleteView, self).post(request)

    def form_valid(self, form: DeleteWithSlugForm):
        if self.breeder.slug == form.cleaned_data['slug']:
            try:
                self.breeder.delete()
                return super(HxBreederDeleteView, self).form_valid(form)
            except Exception as ex:
                print(f"Deleting breeder \"{self.breeder.name}\" failed! ({str(ex)})")
        return redirect(self.get_failed_url())

    def form_invalid(self, form):
        return redirect(self.get_failed_url())


class StrainView(BaseView):
    template_name = settings.GROW_TEMPLATES["grow/strain/strain"]

    def get(self, request: HttpRequest, breeder_slug: str, slug: str) -> HttpResponse:
        breeder = get_object_or_404(Breeder, slug=breeder_slug)
        strain = get_object_or_404(breeder.strains, slug=slug)

        language_code = get_language()

        translation = strain.get_translation(language_code)
        breeder_translation = breeder.get_translation(language_code)
        comments = strain.comments.filter(language_code=language_code).order_by('-created_at')[:10]

        growlogs = [
            growlog_strain.growlog
            for growlog_strain in strain.growlog_strains.all().order_by(Lower('growlog__name'))
            if growlog_user_is_allowed_to_view(self.request.user, growlog_strain.growlog)
        ]
        allowed_to_edit = request.user.is_authenticated
        allowed_to_delete = request.user.is_authenticated and strain.growlog_count == 0
        allowed_to_translate = request.user.is_authenticated  # TODO: add logic

        return render(request, self.template_name, context={
            'strain': strain,
            'growlogs': growlogs,
            'allowed_to_delete': allowed_to_delete,
            'allowed_to_edit': allowed_to_edit,
            'allowed_to_translate': allowed_to_translate,
            'regular_seeds_in_stock': (
                strain.get_regular_seeds_in_stock(self.request.user)
                if self.request.user.is_authenticated else 0
            ),
            'regular_seeds_purchased_on': (
                strain.get_regular_seeds_purchased_on(self.request.user)
                if self.request.user.is_authenticated else None
            ),
            'feminized_seeds_in_stock': (
                strain.get_feminized_seeds_in_stock(self.request.user)
                if self.request.user.is_authenticated else 0
            ),
            'feminized_seeds_purchased_on': (
                strain.get_feminized_seeds_purchased_on(self.request.user)
                if self.request.user.is_authenticated else None
            ),
            'total_seeds_in_stock': strain.get_total_seeds_in_stock(self.request.user) if self.request.user.is_authenticated else 0,  # noqa: E501
            'strain_images': strain.images.all().order_by('-uploaded_at')[:3],
            'strain_translation': translation,
            'strain_url': (translation.strain_url
                           if translation and translation.strain_url
                           else strain.strain_url),
            'seedfinder_url': (translation.seedfinder_url
                               if translation and translation.seedfinder_url
                               else strain.seedfinder_url),
            'description_html': (translation.description_html
                                 if translation and translation.description
                                 else strain.description_html),
            'strain_name': translation.name if translation and translation.name else strain.name,
            'breeder_translation': breeder_translation,
            'breeder_url': (breeder_translation.breeder_url
                            if breeder_translation and breeder_translation.breeder_url
                            else breeder.breeder_url),
            'seedfinder_breeder_url': (breeder_translation.seedfinder_url
                                       if breeder_translation and breeder_translation.seedfinder_url
                                       else breeder.seedfinder_url),
            'breeder_name': (breeder_translation.name
                             if breeder_translation and breeder_translation.name
                             else breeder.name),
            'comments': comments,
            'translation': translation,
        })


class StrainCreateView(LoginRequiredMixin, View):
    template_name = settings.GROW_TEMPLATES["grow/strain/create"]

    def get(self, request: HttpRequest, breeder_pk: int) -> HttpResponse:
        breeder = get_object_or_404(Breeder, pk=breeder_pk)

        return render(request, self.template_name, context={
            'breeder': breeder,
            'form': StrainForm(),
        })

    def post(self, request: HttpRequest, breeder_pk: int) -> HttpResponse:
        breeder = get_object_or_404(Breeder, pk=breeder_pk)
        form = StrainForm(request.POST)

        if form.is_valid():
            strain = form.save(commit=False)
            if form.cleaned_data['flowering_time_unit'] == 'w':
                strain.flowering_time_days = strain.flowering_time_days * 7
            strain.created_by = self.request.user
            strain.breeder = breeder
            strain.save()

            return redirect(reverse("grow:strain-detail", kwargs={
                'breeder_slug': breeder.slug,
                'slug': strain.slug,
            }))

        return render(request, self.template_name, context={
            'breeder': breeder,
            'form': form,
        })


class StrainUpdateView(LoginRequiredMixin, View):
    template_name = settings.GROW_TEMPLATES["grow/strain/strain/update"]

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.strain = get_object_or_404(Strain, pk=pk)
        return render(request, self.template_name, context={
            'breeder': self.strain.breeder,
            'form': StrainForm(instance=self.strain)
        })

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.strain = get_object_or_404(Strain, pk=pk)

        form = StrainForm(request.POST, instance=self.strain)

        if form.is_valid():
            strain = form.save(commit=False)
            if form.cleaned_data['flowering_time_unit'] == 'w':
                strain.flowering_time_days = strain.flowering_time_days * 7
            strain.save()

            return redirect(reverse("grow:strain-detail", kwargs={
                'breeder_slug': strain.breeder.slug,
                'slug': strain.slug,
            }))

        form.fields['name'] = self.strain.name

        return render(request, self.template_name, context={
            'breeder': self.strain.breeder,
            'form': form,
        })


class StrainDeleteView(LoginRequiredMixin, FormView):
    template_name = settings.GROW_TEMPLATES['grow/strain/delete']
    form_class = DeleteWithSlugForm

    def get_success_url(self):
        return reverse('grow:breeder-detail', kwargs={'slug': self.strain.breeder.slug})

    def get_failed_url(self):
        return reverse('grow:strain-detail', kwargs={
            'breeder_slug': self.strain.breeder.slug,
            'slug': self.strain.slug,
        })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['strain'] = self.strain
        return context

    def form_valid(self, form: DeleteWithSlugForm) -> HttpResponse:
        if self.strain.slug == form.cleaned_data['slug']:
            try:
                self.strain.delete()
            except Exception as ex:
                print(f"Unable to delete strain {self.strain.name}! ({ex})")
            return super(StrainDeleteView, self).form_valid(form)
        return self.get_failed_url()

    def form_invalid(self, form):
        return self.get_failed_url()

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.strain = get_object_or_404(Strain, pk=pk)
        return super(StrainDeleteView, self).get(request)

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.strain = get_object_or_404(Strain, pk=pk)
        return super(StrainDeleteView, self).post(request)


class HxStrainDeleteView(LoginRequiredMixin, FormView):
    template_name = settings.GROW_TEMPLATES['grow/strain/hx/delete']
    form_class = DeleteWithSlugForm

    def get_success_url(self):
        return reverse('grow:breeder-detail', kwargs={'slug': self.strain.breeder.slug})

    def get_failed_url(self):
        return reverse('grow:strain-detail', kwargs={
            'breeder_slug': self.strain.breeder.slug,
            'slug': self.strain.slug,
        })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['strain'] = self.strain
        return context

    def form_valid(self, form: DeleteWithSlugForm) -> HttpResponse:
        if self.strain.slug == form.cleaned_data['slug']:
            try:
                self.strain.delete()
            except Exception as ex:
                print(f"Unable to delete strain {self.strain.name}! ({ex})")
            return super(HxStrainDeleteView, self).form_valid(form)
        return self.get_failed_url()

    def form_invalid(self, form):
        return self.get_failed_url()

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.strain = get_object_or_404(Strain, pk=pk)
        return super(HxStrainDeleteView, self).get(request)

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.strain = get_object_or_404(Strain, pk=pk)
        return super(HxStrainDeleteView, self).post(request)


class StrainAddToStockView(LoginRequiredMixin, FormView):
    template_name = settings.GROW_TEMPLATES['grow/strain/strain/add_to_stock']
    form_class = StrainAddToStockForm

    def get_context_data(self, **kwargs):
        context = super(StrainAddToStockView, self).get_context_data(**kwargs)
        context['strain'] = self.strain
        context['feminized'] = self.feminized
        try:
            context['seeds_in_stock'] = self.strain.seeds_in_stock.get(is_feminized=self.feminized)
        except StrainsInStock.DoesNotExist:
            context['seeds_in_stock'] = 0

        return context

    def get_success_url(self) -> str:
        return reverse('grow:strain-detail', kwargs={
            'breeder_slug': self.strain.breeder.slug,
            'slug': self.strain.slug
        })

    def form_valid(self, form: StrainAddToStockForm):
        print("Form is valid!")
        year = form.cleaned_data['purchased_on_year']
        month = form.cleaned_data['purchased_on_month']
        day = form.cleaned_data['purchased_on_day']

        def sanitize_day() -> int:
            import calendar
            if year and month and day:
                last_day_of_month = calendar.monthrange(year, month)[1]
                if day > last_day_of_month:
                    return last_day_of_month
            return day

        purchased_on = date(year, month, sanitize_day()) if year and month and day else None

        if self.feminized:
            self.strain.add_feminized_seeds_to_stock(
                self.request.user,
                form.cleaned_data['quantity'],
                purchased_on=purchased_on,
                notes_type=form.cleaned_data['notes_type'],
                notes=form.cleaned_data['notes'],
            )
        else:
            self.strain.add_regular_seeds_to_stock(
                self.request.user,
                form.cleaned_data['quantity'],
                purchased_on=purchased_on,
                notes_type=form.cleaned_data['notes_type'],
                notes=form.cleaned_data['notes'],
            )

        return redirect(self.get_success_url())

    def form_invalid(self, form):
        print(form.errors)
        return super(StrainAddToStockView, self).form_invalid(form)

    def get(self, request: HttpRequest, strain: int, feminized: int) -> HttpResponse:
        self.strain = get_object_or_404(Strain, pk=strain)
        self.feminized = bool(feminized)

        return super(StrainAddToStockView, self).get(request)

    def post(self, request: HttpRequest, strain: int, feminized: int) -> HttpResponse:
        self.strain = get_object_or_404(Strain, pk=strain)
        self.feminized = bool(feminized)

        return super(StrainAddToStockView, self).post(request)


class StrainRemoveFromStockView(LoginRequiredMixin, FormView):
    template_name = settings.GROW_TEMPLATES['grow/strain/strain/remove_from_stock']
    invalid_template_name = settings.GROW_TEMPLATES['grow/strain/strain/remove_from_stock_invalid']
    form_class = StrainRemoveFromStockForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['strain'] = self.strain
        context['feminized'] = self.feminized
        context['feminized_int'] = 1 if self.feminized else 0
        context['n_seeds_in_stock'] = self.n_seeds_in_stock

        return context

    def get_form(self, form_class=StrainRemoveFromStockForm):
        form = form_class()
        form.fields['quantity'].max_value = self.n_seeds_in_stock
        return form

    def get_success_url(self):
        return reverse('grow:strain-detail', kwargs={
            'breeder_slug': self.strain.breeder.slug,
            'slug': self.strain.slug
        })

    def form_valid(self, form: StrainRemoveFromStockForm):
        print(self.feminized)
        if self.feminized:
            self.strain.remove_feminized_seeds_from_stock(
                self.request.user,
                form.cleaned_data['quantity']
            )
        else:
            self.strain.remove_regualar_seeds_from_stock(
                self.request.user,
                form.cleaned_data['quantity']
            )
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        print("Form is invalid!")
        print(form.errors)
        return super().form_invalid(form)

    def validate(self):
        if self.n_seeds_in_stock > 0:
            return True
        return False

    def get(self, request: HttpRequest, strain: int, feminized: int) -> HttpResponse:
        self.strain = get_object_or_404(Strain, pk=strain)
        self.feminized = bool(feminized)

        if self.feminized:
            self.n_seeds_in_stock = self.strain.get_feminized_seeds_in_stock(self.request.user)
        else:
            self.n_seeds_in_stock = self.strain.get_regular_seeds_in_stock(self.request.user)

        if not self.validate():
            return render(request, self.invalid_template_name, context=self.get_context_data())

        return super(StrainRemoveFromStockView, self).get(request)

    def post(self, request: HttpRequest, strain: int, feminized: int) -> HttpResponse:
        print("POST request handler")
        self.strain = get_object_or_404(Strain, pk=strain)
        self.feminized = bool(feminized)

        if self.feminized:
            self.n_seeds_in_stock = self.strain.get_feminized_seeds_in_stock(self.request.user)
        else:
            self.n_seeds_in_stock = self.strain.get_regular_seeds_in_stock(self.request.user)

        if not self.validate():
            return render(request, self.invalid_template_name, context=self.get_context_data())

        form = self.get_form_class()(request.POST)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class HxStrainAddToStockView(LoginRequiredMixin, FormView):
    template_name = settings.GROW_TEMPLATES['grow/strain/strain/hx/add_to_stock']
    update_template_name = settings.GROW_TEMPLATES['grow/strain/strain/in_stock/hx/update']  # noqa: E501

    form_class = StrainAddToStockForm

    def get_context_data(self, **kwargs):
        context = super(HxStrainAddToStockView, self).get_context_data(**kwargs)
        context['strain'] = self.strain
        context['feminized'] = self.feminized

        if self.feminized:
            context['n_seeds_in_stock'] = self.strain.get_feminized_seeds_in_stock(self.request.user)  # noqa: E501
        else:
            context['n_seeds_in_stock'] = self.strain.get_regular_seeds_in_stock(self.request.user)

        return context

    def get_form(self, form_class=StrainAddToStockForm):
        try:
            sis = self.strain.seeds_in_stock.get(user=self.request.user,
                                                 is_feminized=self.feminized)
            today = date.today()
            form = form_class(initial={
                'purchased_on_year': sis.purchased_on.year if sis.purchased_on else today.year,
                'purchased_on_month': sis.purchased_on.month if sis.purchased_on else today.month,
                'purchased_on_day': sis.purchased_on.day if sis.purchased_on else today.day,
                'quantity': 1,
                'notes_type': sis.notes_type,
                'notes': sis.notes,
            })
        except StrainsInStock.DoesNotExist:
            form = form_class(initial={'quantity': 1})
        return form

    def get_success_url(self) -> str:
        return reverse('grow:strain-detail', kwargs={
            'breeder_slug': self.strain.breeder.slug,
            'slug': self.strain.slug
        })

    def form_valid(self, form: StrainAddToStockForm):
        print("Form is valid!")
        year = int(form.cleaned_data['purchased_on_year'])
        month = int(form.cleaned_data['purchased_on_month'])
        day = int(form.cleaned_data['purchased_on_day'])

        print(year, month, day)

        def sanitize_day() -> int:
            import calendar
            if year and month and day:
                last_day_of_month = calendar.monthrange(year, month)[1]
                if day > last_day_of_month:
                    return last_day_of_month
            return day

        purchased_on = date(year, month, sanitize_day()) if year and month and day else None

        print("Notes:", form.cleaned_data['notes'])

        if self.feminized:
            self.strain.add_feminized_seeds_to_stock(
                self.request.user,
                form.cleaned_data['quantity'],
                purchased_on=purchased_on,
                notes_type=form.cleaned_data['notes_type'],
                notes=form.cleaned_data['notes'],
            )
        else:
            self.strain.add_regular_seeds_to_stock(
                self.request.user,
                form.cleaned_data['quantity'],
                purchased_on=purchased_on,
                notes_type=form.cleaned_data['notes_type'],
                notes=form.cleaned_data['notes'],
            )
        return render(self.request, self.update_template_name, context=self.get_context_data(
            success=True,
            seeds_added=True,
            regular_seeds_in_stock=self.strain.get_regular_seeds_in_stock(self.request.user),
            feminized_seeds_in_stock=self.strain.get_feminized_seeds_in_stock(self.request.user),
            total_seeds_in_stock=self.strain.get_total_seeds_in_stock(self.request.user),
            feminized_seeds_purchased_on=self.strain.get_feminized_seeds_purchased_on(self.request.user),  # noqa: E501
            regular_seeds_purchased_on=self.strain.get_regular_seeds_purchased_on(self.request.user),  # noqa: E501
        ))

    def form_invalid(self, form):
        print("form invalid handler")
        print(form.errors)
        return render(self.request, self.update_template_name, context=self.get_context_data(
            success=False,
            seeds_added=True,
            regular_seeds_in_stock=self.strain.get_regular_seeds_in_stock(self.request.user),
            feminized_seeds_in_stock=self.strain.get_feminized_seeds_in_stock(self.request.user),
            total_seeds_in_stock=self.strain.get_total_seeds_in_stock(self.request.user),
            feminized_seeds_purchased_on=self.strain.get_feminized_seeds_purchased_on(self.request.user),  # noqa: E501
            regular_seeds_purchased_on=self.strain.get_regular_seeds_purchased_on(self.request.user),  # noqa: E501
        ))

    def get(self, request: HttpRequest, strain: int, feminized: int) -> HttpResponse:
        self.strain = get_object_or_404(Strain, pk=strain)
        self.feminized = bool(feminized)

        return super(HxStrainAddToStockView, self).get(request)

    def post(self, request: HttpRequest, strain: int, feminized: int) -> HttpResponse:
        self.strain = get_object_or_404(Strain, pk=strain)
        self.feminized = bool(feminized)

        form = self.get_form_class()(request.POST)

        if form.is_valid():
            print("Form is valid!")
            return self.form_valid(form)
        else:
            print("Form is invalid!")
            return self.form_invalid(form)


class HxStrainRemoveFromStockView(LoginRequiredMixin, FormView):
    template_name = settings.GROW_TEMPLATES['grow/strain/strain/in_stock/hx/remove']
    invalid_template_name = settings.GROW_TEMPLATES['grow/strain/strain/in_stock/hx/remove_invalid']
    update_template_name = settings.GROW_TEMPLATES['grow/strain/strain/in_stock/hx/update']  # noqa: E501

    form_class = StrainRemoveFromStockForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['strain'] = self.strain
        context['feminized'] = self.feminized
        context['feminized_int'] = 1 if self.feminized else 0
        context['n_seeds_in_stock'] = self.n_seeds_in_stock

        return context

    def get_form(self, form_class=StrainRemoveFromStockForm):
        form = form_class()
        form.fields['quantity'].max_value = self.n_seeds_in_stock
        return form

    def get_success_url(self):
        return reverse('grow:strain-detail', kwargs={
            'breeder_slug': self.strain.breeder.slug,
            'slug': self.strain.slug
        })

    def form_valid(self, form: StrainRemoveFromStockForm):
        print(self.feminized)
        if self.feminized:
            self.strain.remove_feminized_seeds_from_stock(
                self.request.user,
                form.cleaned_data['quantity']
            )
        else:
            self.strain.remove_regualar_seeds_from_stock(
                self.request.user,
                form.cleaned_data['quantity']
            )
        return render(self.request, self.update_template_name, context=self.get_context_data(
            success=True,
            seeds_removed=True,
            regular_seeds_in_stock=self.strain.get_regular_seeds_in_stock(self.request.user),
            feminized_seeds_in_stock=self.strain.get_feminized_seeds_in_stock(self.request.user),
            total_seeds_in_stock=self.strain.get_total_seeds_in_stock(self.request.user),
            feminized_seeds_purchased_on=self.strain.get_feminized_seeds_purchased_on(self.request.user),  # noqa: E501
            regular_seeds_purchased_on=self.strain.get_regular_seeds_purchased_on(self.request.user),  # noqa: E501
        ))

    def form_invalid(self, form):
        print("Form is invalid!")
        print(form.errors)
        return render(self.request, self.update_template_name, context=self.get_context_data(
            success=False,
            seeds_added=False,
            regular_seeds_in_stock=self.strain.get_regular_seeds_in_stock(self.request.user),
            feminized_seeds_in_stock=self.strain.get_feminized_seeds_in_stock(self.request.user),
            total_seeds_in_stock=self.strain.get_total_seeds_in_stock(self.request.user),
            feminized_seeds_purchased_on=self.strain.get_feminized_seeds_purchased_on(self.request.user),  # noqa: E501
            regular_seeds_purchased_on=self.strain.get_regular_seeds_purchased_on(self.request.user),  # noqa: E501
        ))

    def validate(self):
        if self.n_seeds_in_stock > 0:
            return True
        return False

    def get(self, request: HttpRequest, strain: int, feminized: int) -> HttpResponse:
        self.strain = get_object_or_404(Strain, pk=strain)
        self.feminized = bool(feminized)

        if self.feminized:
            self.n_seeds_in_stock = self.strain.get_feminized_seeds_in_stock(self.request.user)
        else:
            self.n_seeds_in_stock = self.strain.get_regular_seeds_in_stock(self.request.user)

        if not self.validate():
            return render(request, self.invalid_template_name, context=self.get_context_data())

        return super(HxStrainRemoveFromStockView, self).get(request)

    def post(self, request: HttpRequest, strain: int, feminized: int) -> HttpResponse:
        print("POST request handler")
        self.strain = get_object_or_404(Strain, pk=strain)
        self.feminized = bool(feminized)

        if self.feminized:
            self.n_seeds_in_stock = self.strain.get_feminized_seeds_in_stock(self.request.user)
        else:
            self.n_seeds_in_stock = self.strain.get_regular_seeds_in_stock(self.request.user)

        if not self.validate():
            return render(request, self.invalid_template_name, context=self.get_context_data())

        form = self.get_form_class()(request.POST)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class StrainSearchView(BaseView):
    template_name = settings.GROW_TEMPLATES['grow/strain/strain_search_results']

    def post(self, request: HttpRequest) -> HttpResponse:
        form = StrainSearchForm(request.POST)
        if form.is_valid():
            search_query = form.cleaned_data['search_query']
        else:
            search_query = None

        if not search_query:
            return redirect(reverse('grow:breeder-overview'))

        strains = Strain.objects.filter(name__icontains=search_query).order_by(Lower("name")).order_by(Lower("breeder__name"), Lower("name"))  # noqa: E501

        return render(request, self.template_name, context={
            'strains': strains
        })


class StrainImageUploadView(LoginRequiredMixin, View):
    template_name = settings.GROW_TEMPLATES['grow/strain/strain/image_upload']

    def get(self, request: HttpRequest, strain_pk: int) -> HttpResponse:
        strain = get_object_or_404(Strain, pk=strain_pk)

        return render(request, self.template_name, context={
            'strain': strain,
            'form': StrainImageUploadForm(),
        })

    def post(self, request: HttpRequest, strain_pk: int) -> HttpResponse:
        strain = get_object_or_404(Strain, pk=strain_pk)
        form = StrainImageUploadForm(request.POST, request.FILES)

        if form.is_valid():
            strain_image = form.save(commit=False)
            strain_image.strain = strain
            strain_image.uploader = request.user
            strain_image.save()

            return redirect(reverse("grow:strain-detail", kwargs={
                'breeder_slug': strain.breeder.slug,
                'slug': strain.slug,
            }))

        print("form invalid")
        print(form.errors)
        return render(request, self.template_name, context={
            'strain': strain,
            'form': form,
        })


class BreederTranslationView(LoginRequiredMixin, View):
    template_name = settings.GROW_TEMPLATES['grow/breeder/translation']

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        breeder = get_object_or_404(Breeder, pk=pk)
        lang_code = get_language()
        if not lang_code.startswith('en'):
            lang_code = lang_code.split('-')[0]

        short_lang_code = lang_code.split('-')[0]

        seedfinder_url = breeder.seedfinder_url

        if short_lang_code in ['de', 'fr', 'es', 'en']:
            if breeder.seedfinder_url:
                seedfinder_url = re.sub('(/en/|/de/|/fr/|/es/)',
                                        f'/{short_lang_code}/',
                                        breeder.seedfinder_url)

        existing_translation = breeder.translations.filter(language_code=lang_code).first()

        if existing_translation:
            form = BreederTranslationForm(instance=existing_translation)
        else:
            form = BreederTranslationForm(initial={
                'language_code': lang_code,
                'name': breeder.name,
                'breeder_url': breeder.breeder_url,
                'seedfinder_url': seedfinder_url})

        return render(request, self.template_name, context={
            'breeder': breeder,
            'form': form,
        })

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        breeder = get_object_or_404(Breeder, pk=pk)

        language_code = request.POST.get('language_code').strip()
        if not (re.match(r'^[a-z]{2}(-[a-z]{2})?$', language_code)):
            raise Http404("Invalid language code format!")

        existing_translation = breeder.translations.filter(language_code=language_code).first()
        if existing_translation:
            form = BreederTranslationForm(request.POST, instance=existing_translation)
        else:
            form = BreederTranslationForm(request.POST)

        if form.is_valid():
            translation = form.save(commit=False)
            translation.breeder = breeder
            translation.name = form.cleaned_data['name']
            translation.breeder_url = form.cleaned_data['breeder_url']
            translation.seedfinder_url = form.cleaned_data['seedfinder_url']
            if not existing_translation:
                translation.user = request.user
            translation.edited_by = request.user
            translation.language_code = form.cleaned_data['language_code']
            translation.description = form.cleaned_data['description']
            translation.description_type_data = form.cleaned_data['description_type_data']
            translation.save()

            return redirect(reverse("grow:breeder-detail", kwargs={
                'slug': breeder.slug,
            }))
        else:
            print("form invalid")
            print(form.errors)

        return render(request, self.template_name, context={
            'breeder': breeder,
            'form': form,
        })


class HxBreederTranslationView(LoginRequiredMixin, View):
    template_name = settings.GROW_TEMPLATES['grow/breeder/hx/translation']

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        breeder = get_object_or_404(Breeder, pk=pk)
        if 'lang_code' not in request.GET:
            lang_code = get_language()
        else:
            lang_code = request.GET.get('lang_code')
            if not (re.match(r'^[a-z]{2}(-[a-z]{2})?$', lang_code)):
                raise Http404("Invalid language code format!")

        if not lang_code.startswith('en'):
            lang_code = lang_code.split('-')[0]

        existing_translation = breeder.translations.filter(language_code=lang_code).first()

        if existing_translation:
            form = BreederTranslationForm(instance=existing_translation)
        else:
            short_lang_code = lang_code.split('-')[0]

            seedfinder_url = breeder.seedfinder_url

            if short_lang_code in ['de', 'fr', 'es', 'en']:
                if breeder.seedfinder_url:
                    seedfinder_url = re.sub('(/en/|/de/|/fr/|/es/)',
                                            f'/{short_lang_code}/',
                                            breeder.seedfinder_url)

                form = BreederTranslationForm(initial={
                    'language_code': lang_code,
                    'name': breeder.name,
                    'breeder_url': breeder.breeder_url,
                    'seedfinder_url': seedfinder_url
                })

        return render(request, self.template_name, context={
            'breeder': breeder,
            'form': form,
        })


class StrainTranslationView(LoginRequiredMixin, View):
    template_name = settings.GROW_TEMPLATES['grow/strain/strain/translation']

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        strain = get_object_or_404(Strain, pk=pk)

        lang_code = get_language()
        if not lang_code.startswith('en'):
            lang_code = lang_code.split('-')[0]

        existing_translation = strain.translations.filter(language_code=lang_code).first()

        short_lang_code = lang_code.split('-')[0]
        seedfinder_url = strain.seedfinder_url
        if short_lang_code in ['de', 'fr', 'es', 'en']:
            if strain.seedfinder_url:
                seedfinder_url = re.sub('(/en/|/de/|/fr/|/es/)',
                                        f'/{short_lang_code}/',
                                        strain.seedfinder_url)  # noqa: E501

        if existing_translation:
            form = StrainTranslationForm(instance=existing_translation)
        else:
            form = StrainTranslationForm(initial={
                'language_code': lang_code,
                'name': strain.name,
                'strain_url': strain.strain_url,
                'seedfinder_url': seedfinder_url,
            })

        return render(request, self.template_name, context={
            'strain': strain,
            'form': form,
        })

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        strain = get_object_or_404(Strain, pk=pk)

        language_code = request.POST.get('language_code').strip()
        if not (re.match(r'^[a-z]{2}(-[a-z]{2})?$', language_code)):
            raise Http404("Invalid language code format!")

        existing_translation = strain.translations.filter(language_code=language_code).first()

        if existing_translation:
            form = StrainTranslationForm(request.POST, instance=existing_translation)
        else:
            form = StrainTranslationForm(request.POST)

        if form.is_valid():
            translation = form.save(commit=False)
            translation.strain = strain
            if not existing_translation:
                translation.user = request.user
            translation.edited_by = request.user
            translation.language_code = form.cleaned_data['language_code']
            translation.name = form.cleaned_data['name']
            translation.description = form.cleaned_data['description']
            translation.description_type_data = form.cleaned_data['description_type_data']
            translation.save()

            return redirect(reverse("grow:strain-detail", kwargs={
                'breeder_slug': strain.breeder.slug,
                'slug': strain.slug,
            }))

        return render(request, self.template_name, context={
            'strain': strain,
            'form': form,
        })


class HxStrainTranslationView(LoginRequiredMixin, View):
    template_name = settings.GROW_TEMPLATES['grow/strain/strain/hx/translation']

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        strain = get_object_or_404(Strain, pk=pk)

        if 'lang_code' not in request.GET:
            lang_code = get_language()
        else:
            lang_code = request.GET.get('lang_code')
            if not (re.match(r'^[a-z]{2}(-[a-z]{2})?$', lang_code)):
                raise Http404("Invalid language code format!")

        if not lang_code.startswith('en'):
            lang_code = lang_code.split('-')[0]

        existing_translation = strain.translations.filter(language_code=lang_code).first()

        short_lang_code = lang_code.split('-')[0]
        seedfinder_url = strain.seedfinder_url
        if short_lang_code in ['de', 'fr', 'es', 'en']:
            if strain.seedfinder_url:
                seedfinder_url = re.sub('(/en/|/de/|/fr/|/es/)', f'/{short_lang_code}/',
                                        strain.seedfinder_url)

        if existing_translation:
            form = StrainTranslationForm(instance=existing_translation)
        else:
            form = StrainTranslationForm(initial={
                'language_code': lang_code,
                'name': strain.name,
                'strain_url': strain.strain_url,
                'seedfinder_url': seedfinder_url,
            })

        return render(request, self.template_name, context={
            'strain': strain,
            'form': form,
        })


class StrainCommentCreateView(LoginRequiredMixin, View):
    template_name = settings.GROW_TEMPLATES['grow/strain/strain/comment_create']

    def get(self, request: HttpRequest, strain_pk: int) -> HttpResponse:
        strain = get_object_or_404(Strain, pk=strain_pk)

        return render(request, self.template_name, context={
            'strain': strain,
            'form': StrainCommentForm(),
        })

    def post(self, request: HttpRequest, strain_pk: int) -> HttpResponse:
        strain = get_object_or_404(Strain, pk=strain_pk)
        form = StrainCommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.strain = strain
            comment.user = request.user
            comment.save()

            return redirect(reverse("grow:strain-detail", kwargs={
                'breeder_slug': strain.breeder.slug,
                'slug': strain.slug,
            }))

        return render(request, self.template_name, context={
            'strain': strain,
            'form': form
        })


class StrainCommentUpdateView(LoginRequiredMixin, View):
    template_name = settings.GROW_TEMPLATES['grow/strain/strain/comment_update']

    def get(self, request: HttpRequest, comment_pk: int) -> HttpResponse:
        comment = get_object_or_404(StrainUserComment, pk=comment_pk)

        if not request.user == comment.user:
            raise Http404("You do not have permission to edit this comment!")

        return render(request, self.template_name, context={
            'strain': comment.strain,
            'form': StrainCommentForm(instance=comment),
        })

    def post(self, request: HttpRequest, comment_pk: int) -> HttpResponse:
        comment = get_object_or_404(StrainUserComment, pk=comment_pk)
        form = StrainCommentForm(request.POST, instance=comment)

        if not request.user == comment.user:
            raise Http404("You do not have permission to edit this comment!")

        if form.is_valid():
            form.save()

            return redirect(reverse("grow:strain-detail", kwargs={
                'breeder_slug': comment.strain.breeder.slug,
                'slug': comment.strain.slug,
            }))

        return render(request, self.template_name, context={
            'strain': comment.strain,
            'form': form
        })


class StrainGalleryView(View):
    template_name = settings.GROW_TEMPLATES['grow/strain/gallery']

    def get(self, request: HttpRequest, strain_pk: int) -> HttpResponse:
        self.strain = get_object_or_404(Strain, pk=strain_pk)
        self.strain_images = self.strain.images.order_by('-uploaded_at')

        return render(request, self.template_name, context={
            'strain': self.strain,
            'strain_images': self.strain_images,
        })


class StrainGallerySlidesView(View):
    template_name = settings.GROW_TEMPLATES['grow/strain/gallery/slides']

    def get(self, request: HttpRequest, strain_pk: int) -> HttpResponse:
        strain = get_object_or_404(Strain, pk=strain_pk)
        strain_images = strain.images.order_by('-uploaded_at')
        first_image = strain_images.first() if strain_images else None

        return render(request, self.template_name, context={
            'strain': strain,
            'strain_images': strain_images,
            'n_strain_images': strain_images.count(),
            'first_image': first_image,
            'use_bootstrap': True,
        })


class HxStrainSearchView(BaseView):
    template_name = settings.GROW_TEMPLATES['grow/strain/hx/search']

    def get(self, request: HttpRequest) -> HttpResponse:
        form = StrainSearchForm()

        return render(request, self.template_name, context={
            'form': form,
        })


class HxStrainStockNotesView(LoginRequiredMixin, BaseView):
    template_name = settings.GROW_TEMPLATES['grow/strain/strain/in_stock/hx/notes']

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        try:
            sis = StrainsInStock.objects.get(pk=pk)
        except StrainsInStock.DoesNotExist:
            sis = None

        except StrainsInStock.DoesNotExist:
            raise Http404("Stock notes not found!")

        return render(request, self.template_name, context={
            'seeds_in_stock': sis,
        })


class StrainAddToStock2View(LoginRequiredMixin, FormView):
    template_name = settings.GROW_TEMPLATES['grow/strain/strain/add_to_stock2']
    success_template_name = settings.GROW_TEMPLATES['grow/strain/strain']

    form_class = StrainAddToStock2Form

    def get_success_url(self):
        return reverse('grow:user-info')

    def form_valid(self, form):
        print("Form is valid!")
        return super(StrainAddToStock2View, self).form_valid(form)

    def form_invalid(self, form):
        print("Form is invalid!")
        print(form.errors)
        super(StrainAddToStock2View, self).form_invalid(form)
        return render(self.request, self.success_template_name,
                      context=self.get_context_data(form=form))


class HxStrainAddToStock2View(StrainAddToStock2View):
    template_name = settings.GROW_TEMPLATES['grow/strain/strain/hx/add_to_stock2']
    info_template_name = settings.GROW_TEMPLATES['grow/seeds_in_stock/hx/info']

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name, self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sis = self.request.user.seeds_in_stock.all().order_by('strain__name',
                                                              'strain__breeder__name',
                                                              'is_feminized')
        n_seeds_in_stock = 0
        n_feminized_seeds_in_stock = 0
        n_regular_seeds_in_stock = 0

        for in_stock in sis:
            n_seeds_in_stock += in_stock.quantity
            if in_stock.is_feminized:
                n_feminized_seeds_in_stock += in_stock.quantity
            else:
                n_regular_seeds_in_stock += in_stock.quantity

        page = 0
        paginate = settings.GROW_USER_SETTINGS(self.request).paginate
        page = self.request.GET.get('seeds_in_stock_page', self.request.GET.get('page', 1))
        paginate = self.request.GET.get(
            'seeds_in_stock_paginate',
            self.request.GET.get('paginate', settings.GROW_USER_SETTINGS(self.request).paginate)
        )
        n_pages = (sis.count() - 1) // paginate + 1
        if page < 1:
            page = 1
        elif page > n_pages:
            page = n_pages

        breeders = Breeder.objects.annotate(
            strains_count=Count('strains')
        ).filter(strains_count__gt=0).order_by('name')
        breeder = breeders.first() if breeders else None
        if breeder:
            strains = breeder.strains.all().order_by('name')
            strain = strains.first() if strains else None
        else:
            strains = Strain.objects.none()
            strain = None

        form = StrainAddToStock2Form(
            data={
                'breeder': breeder.pk if breeder else None,
                'strain': strain.pk if strain else None,
            }
        )
        form.fields['breeder'].choices = [(b.pk, b.name) for b in breeders]
        form.fields['strain'].choices = [(s.pk, s.name) for s in strains] if strains else []

        context.update({
            'form': kwargs.get('form', StrainAddToStock2Form()),
            'n_seeds_in_stock': n_seeds_in_stock,
            'n_feminized_seeds_in_stock': n_feminized_seeds_in_stock,
            'n_regular_seeds_in_stock': n_regular_seeds_in_stock,
            'seeds_in_stock_current_page': page,
            'seeds_in_stock_paginate': paginate,
            'seeds_in_stock_n_pages': n_pages,
            'seeds_in_stock': sis[(page - 1) * paginate: page * paginate],
        })
        context.update(kwargs)

        return context

    def form_valid(self, form):
        print("Form is valid!xxx")
        try:
            print(form.cleaned_data['strain'])
            strain = Strain.objects.get(pk=int(form.cleaned_data['strain'])
                                        if form.cleaned_data['strain'] else 0)
        except Strain.DoesNotExist:
            print("Strain not found!")
            strain = None
            raise Http404("Strain not found!")

        if strain:
            print("adding seeds to stock")
            if form.cleaned_data['strain_type'] == 'feminized':
                strain.add_feminized_seeds_to_stock(
                    self.request.user,
                    form.cleaned_data['quantity'],
                    purchased_on=date(
                        int(form.cleaned_data['purchased_on_year']),
                        int(form.cleaned_data['purchased_on_month']),
                        int(form.cleaned_data['purchased_on_day'])
                    ) if (
                        form.cleaned_data['purchased_on_year']
                        and form.cleaned_data['purchased_on_month']
                        and form.cleaned_data['purchased_on_day']
                    ) else date.today(),  # noqa: E501
                    notes_type=form.cleaned_data['notes_type'],
                    notes=form.cleaned_data['notes'],
                )
            else:
                strain.add_regular_seeds_to_stock(
                    self.request.user,
                    form.cleaned_data['quantity'],
                    purchased_on=date(
                        form.cleaned_data['purchased_on_year'],
                        form.cleaned_data['purchased_on_month'],
                        form.cleaned_data['purchased_on_day']
                    ) if (
                        form.cleaned_data['purchased_on_year']
                        and form.cleaned_data['purchased_on_month']
                        and form.cleaned_data['purchased_on_day']
                    ) else date.today(),  # noqa: E501
                    notes_type=form.cleaned_data['notes_type'],
                    notes=form.cleaned_data['notes'],
                )

        if form.cleaned_data['strain_type'] == 'feminized' and strain.is_feminized:
            is_feminized_selected = True
        elif form.cleaned_data['strain_type'] == 'regular' and strain.is_regular:
            is_feminized_selected = False

        return render(self.request, self.success_template_name, context=self.get_context_data(
            form=form,
            strain=strain,
            is_feminized=strain.is_feminized,
            is_regular=strain.is_regular,
            is_feminized_selected=is_feminized_selected,
        ))


class StrainUpdateStockView(LoginRequiredMixin, CreateView):
    template_name = settings.GROW_TEMPLATES['grow/strain/strain/add_to_stock']

    form_class = StrainAddToStock2Form

    def get_success_url(self):
        return reverse('grow:strain-detail', kwargs={
            'breeder_slug': self.instance.strain.breeder.slug,
            'slug': self.instance.strain.slug,
        })

    def form_valid(self, form):
        print("Form is valid!")
        self.instance = form.save(commit=False)
        self.instance.user = self.request.user
        return super(StrainUpdateStockView, self).form_valid(form)

    def form_invalid(self, form):
        print("Form is invalid!")
        print(form.errors)
        super(StrainUpdateStockView, self).form_invalid(form)
        return render(self.request, self.success_template_name,
                      context=self.get_context_data(form=form))


class HxSeedsInStockInfoView(LoginRequiredMixin, BaseView):
    template_name = settings.GROW_TEMPLATES['grow/seeds_in_stock/hx/info']

    def get_context_data(self, **kwargs):
        render_table = self.request.GET.get('render_table', '1') == '1'
        render_text = self.request.GET.get('render_text', '0') == '1'
        render_user_text = self.request.GET.get('render_user_text', '0') == '1'

        sis = self.request.user.seeds_in_stock.filter(quantity__gt=0)
        n_sis = sis.count()
        n_seeds_in_stock = 0
        n_feminized_seeds_in_stock = 0
        n_regular_seeds_in_stock = 0

        for in_stock in sis:
            n_seeds_in_stock += in_stock.quantity
            if in_stock.is_feminized:
                n_feminized_seeds_in_stock += in_stock.quantity
            else:
                n_regular_seeds_in_stock += in_stock.quantity

        page = 1
        paginate = settings.GROW_USER_SETTINGS(self.request).paginate
        if 'page' in self.request.GET:
            try:
                page = int(self.request.GET.get('page', page))
            except ValueError:
                pass
        if 'paginate' in self.request.GET:
            paginate = int(self.request.GET.get('paginate', paginate))
        if n_sis < 1:
            n_pages = 1
        else:
            n_pages = (n_sis - 1) // paginate + 1

        page = max(1, min(page, n_pages))
        page -= 1

        context = {
            'n_strains_in_stock': StrainsInStock.objects.filter(user=self.request.user).count(),
            'n_seeds_in_stock': n_seeds_in_stock,
            'n_feminized_seeds_in_stock': n_feminized_seeds_in_stock,
            'n_regular_seeds_in_stock': n_regular_seeds_in_stock,
            'seeds_in_stock_render_table': render_table,
            'seeds_in_stock_render_text': render_text,
            'seeds_in_stock_render_user_text': render_user_text,
            'seeds_in_stock_current_page': page + 1,
            'seeds_in_stock_n_pages': n_pages,
            'seeds_in_stock_paginate': paginate,
            'seeds_in_stock': sis.order_by(
                'strain__name',
                'strain__breeder__name'
            )[(page * paginate):((page + 1) * paginate)],
            'seeds_in_stock_user': kwargs.get('seeds_in_stock_user', self.request.user),
        }
        context.update(kwargs)
        return context

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name, self.get_context_data())


class HxSeedsInStockDialogView(HxSeedsInStockInfoView, HxStrainAddToStock2View):
    form_class = StrainAddToStock2Form
    template_name = settings.GROW_TEMPLATES['grow/seeds_in_stock/hx/dialog']
    info_template_name = settings.GROW_TEMPLATES['grow/seeds_in_stock/hx/info']

    def get_context_data(self, **kwargs):
        context = StrainAddToStock2View.get_context_data(
            self,
            **HxSeedsInStockInfoView.get_context_data(self, **kwargs)
        )
        return context

    def form_valid(self, form):
        HxStrainAddToStock2View.form_valid(self, form)

        return render(self.request, self.info_template_name, context=self.get_context_data(
            form=form,
        ))

    def form_invalid(self, form):
        return render(self.request, self.info_template_name, context=self.get_context_data(
            form=form,
        ))

    def post(self, request: HttpRequest) -> HttpResponse:
        form = self.get_form_class()(request.POST)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class HxSeedsInStockDialogUpdateView(HxSeedsInStockDialogView):
    template_name = settings.GROW_TEMPLATES['grow/seeds_in_stock/hx/dialog']
    form_class = StrainAddToStock2Form

    def sanitize_form(self, form):
        result = StrainAddToStock2Form(
            data={
                'breeder_filter': (
                    form.cleaned_data['breeder_filter']
                    if 'breeder_filter' in form.cleaned_data
                    else None
                ),
                'breeder': (
                    form.fields['breeder'].initial.id
                    if form.fields['breeder'].initial
                    else None
                ),
                'strain_filter': form.cleaned_data['strain_filter'],
                'strain': (
                    form.fields['strain'].initial.id
                    if form.fields['strain'].initial else None
                ),
                'strain_type': form.cleaned_data['strain_type'],
                'quantity': form.cleaned_data['quantity'],
                'purchased_on_year': form.cleaned_data['purchased_on_year'],
                'purchased_on_month': form.cleaned_data['purchased_on_month'],
                'purchased_on_day': form.cleaned_data['purchased_on_day'],
                'notes_type': form.cleaned_data['notes_type'],
                'notes': form.cleaned_data['notes'],
            }
        )
        return result

    def form_valid(self, form: StrainAddToStock2Form):
        return render(self.request, self.template_name, context=self.get_context_data(
            form=self.sanitize_form(form),
        ))

    def form_invalid(self, form: StrainAddToStock2Form):
        return render(self.request, self.template_name, context=self.get_context_data(
            form=self.sanitize_form(form),
        ))

    def post(self, request: HttpRequest) -> HttpResponse:
        form = self.get_form_class()(request.POST)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
