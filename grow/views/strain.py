from datetime import date
import re


from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import get_language
from django.views.generic.edit import CreateView
from django.db.models import Count, Sum
from django.db.models.functions import Lower
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import FormView
from django.db.models import Q
from grow.growapi.models.strain import StrainUserComment

from ._base import BaseView

from ..growapi.models import (
    Breeder,
    Strain,
    StrainsInStock,
)
from .. import settings


from ..forms import (
    DeleteWithSlugForm,
    StrainForm,
    StrainImageUploadForm,
    StrainAddToStockForm,
    StrainAddToStock2Form,
    StrainRemoveFromStockForm,
    StrainSearchForm,
    StrainTranslationForm,
    StrainCommentForm,
)

from ..growapi.permission import growlog_user_is_allowed_to_view

from ..paginator import QuerySetPaginator

import logging
logger = logging.getLogger(__name__)


class HxStrainMyGrowlogsView(View):
    template_name = settings.GROW_TEMPLATES["grow/strain/strain/hx/my_growlogs"]

    def get_context_data(self, **kwargs):
        user_settings = settings.GROW_USER_SETTINGS(self.request)

        try:
            paginate_by = int(self.request.GET.get(
                'my_growlogs_paginate_by',
                self.request.GET.get(
                    'mygl_paginate_by',
                    self.request.GET.get(
                        'mygl_pgn',
                        self.request.GET.get(
                            'paginate_by',
                            self.request.GET.get(
                                'pgn',
                                user_settings.paginate
                            )
                        )
                    )
                )
            ))
        except (ValueError, TypeError):
            paginate_by = user_settings.paginate

        try:
            page = int(self.request.GET.get(
                self.request.GET.get(
                    'my_growlogs_page',
                    self.request.GET.get(
                        'mygl_page',
                        self.request.GET.get(
                            'mygl_p',
                            self.request.GET.get(
                                'page',
                                self.request.GET.get('p', 1)
                            )
                        )
                    )
                )
            ))
        except (ValueError, TypeError):
            page = 1

        if not self.request.user.is_authenticated:
            queryset = self.strain.growlog_strains.filter(grower__isnull=True)
        else:
            queryset = self.strain.growlog_strains.filter(
                growlog__grower=self.request.user.id
            )

        paginator = QuerySetPaginator(queryset,
                                      page=page,
                                      paginate_by=paginate_by,
                                      url_path="grow:hx-strain-growlogs",
                                      url_path_kwargs={"strain_pk": self.strain.pk})

        context = kwargs
        context.setdefault('breeder', self.breeder)
        context.setdefault('strain', self.strain)
        context.setdefault('my_growlogs_paginator', paginator)

        return context

    def get(self, request: HttpRequest, strain_pk: int) -> HttpResponse:
        self.strain = get_object_or_404(Strain, pk=strain_pk)
        self.breeder = self.strain.breeder

        return render(request, self.template_name, context=self.get_context_data())


class HxStrainGrowlogsView(View):
    template_name = settings.GROW_TEMPLATES["grow/strain/strain/hx/growlogs"]

    def get_context_data(self, **kwargs):
        user_settings = settings.GROW_USER_SETTINGS(self.request)
        try:
            paginate_by = int(self.request.GET.get(
                'growlogs_paginate_by',
                self.request.GET.get(
                    'gl_paginate_by',
                    self.request.GET.get(
                        'gl_pgn',
                        self.request.GET.get(
                            'paginate_by',
                            self.request.GET.get(
                                'pgn',
                                user_settings.paginate
                            )
                        )
                    )
                )
            ))
        except (ValueError, TypeError):
            paginate_by = user_settings.paginate

        try:
            page = int(self.request.GET.get(
                self.request.GET.get(
                    'growlogs_page',
                    self.request.GET.get(
                        'gl_page',
                        self.request.GET.get(
                            'gl_p',
                            self.request.GET.get(
                                'page',
                                self.request.GET.get('p', 1)
                            )
                        )
                    )
                )
            ))
        except (ValueError, TypeError):
            page = 1

        growlog_ids = set()

        for growlog_strain in self.strain.growlog_strains.all():
            if (
                self.request.user.is_authenticated
                and growlog_strain.growlog.grower == self.request.user
            ):
                continue

            growlog = growlog_strain.growlog
            if growlog_user_is_allowed_to_view(self.request.user, growlog):
                growlog_ids.add(growlog.pk)

        strain_growlogs = self.strain.growlog_strains.filter(
            growlog__id__in=growlog_ids
        ).order_by('-growlog__started_at')

        paginator = QuerySetPaginator(strain_growlogs,
                                      page=page,
                                      paginate_by=paginate_by,
                                      url_path="grow:hx-strain-my-growlogs",
                                      url_path_kwargs={"strain_pk": self.strain.pk})

        context = kwargs
        context.setdefault('breeder', self.breeder)
        context.setdefault('strain', self.strain)
        context.setdefault('growlogs_paginator', paginator)

        return context

    def get(self, request: HttpRequest, strain_pk: int) -> HttpResponse:
        self.strain = get_object_or_404(Strain, pk=strain_pk)
        self.breeder = self.strain.breeder

        return render(request, self.template_name, self.get_context_data())


class StrainView(HxStrainGrowlogsView, HxStrainMyGrowlogsView, BaseView):
    template_name = settings.GROW_TEMPLATES["grow/strain/strain"]

    def get_context_data(self, **kwargs):
        if self.request.user.is_authenticated:
            return HxStrainMyGrowlogsView.get_context_data(
                self,
                **HxStrainGrowlogsView.get_context_data(self, **kwargs)
            )
        return HxStrainGrowlogsView.get_context_data(self, **kwargs)

    def get(self, request: HttpRequest, breeder_slug: str, slug: str) -> HttpResponse:
        self.breeder = get_object_or_404(Breeder, slug=breeder_slug)
        self.strain = get_object_or_404(self.breeder.strains, slug=slug)

        language_code = get_language()

        translation = self.strain.get_translation(language_code)
        breeder_translation = self.breeder.get_translation(language_code)
        comments = self.strain.comments.filter(
            language_code=language_code
        ).order_by('-created_at')[:10]

        allowed_to_edit = request.user.is_authenticated
        allowed_to_delete = request.user.is_authenticated and self.strain.growlog_count == 0
        allowed_to_translate = request.user.is_authenticated  # TODO: add logic

        return render(request, self.template_name, self.get_context_data(**{
            'allowed_to_delete': allowed_to_delete,
            'allowed_to_edit': allowed_to_edit,
            'allowed_to_translate': allowed_to_translate,
            'regular_seeds_in_stock': (
                self.strain.get_regular_seeds_in_stock(self.request.user)
                if self.request.user.is_authenticated else 0
            ),
            'regular_seeds_purchased_on': (
                self.strain.get_regular_seeds_purchased_on(self.request.user)
                if self.request.user.is_authenticated else None
            ),
            'feminized_seeds_in_stock': (
                self.strain.get_feminized_seeds_in_stock(self.request.user)
                if self.request.user.is_authenticated else 0
            ),
            'feminized_seeds_purchased_on': (
                self.strain.get_feminized_seeds_purchased_on(self.request.user)
                if self.request.user.is_authenticated else None
            ),
            'total_seeds_in_stock': (
                self.strain.get_total_seeds_in_stock(self.request.user)
                if self.request.user.is_authenticated
                else 0
            ),
            'strain_images': self.strain.images.all().order_by('-uploaded_at')[:3],
            'strain_translation': translation,
            'strain_url': (translation.strain_url
                           if translation and translation.strain_url
                           else self.strain.strain_url),
            'seedfinder_url': (translation.seedfinder_url
                               if translation and translation.seedfinder_url
                               else self.strain.seedfinder_url),
            'description_html': (translation.description_html
                                 if translation and translation.description
                                 else self.strain.description_html),
            'strain_name': (
                translation.name
                if translation and translation.name
                else self.strain.name
            ),
            'breeder_translation': breeder_translation,
            'breeder_url': (breeder_translation.breeder_url
                            if breeder_translation and breeder_translation.breeder_url
                            else self.breeder.breeder_url),
            'seedfinder_breeder_url': (breeder_translation.seedfinder_url
                                       if breeder_translation and breeder_translation.seedfinder_url
                                       else self.breeder.seedfinder_url),
            'breeder_name': (breeder_translation.name
                             if breeder_translation and breeder_translation.name
                             else self.breeder.name),
            'comments': comments,
            'translation': translation,
        }))


class StrainCreateView(LoginRequiredMixin, View):
    template_name = settings.GROW_TEMPLATES["grow/strain/create"]
    form_template = settings.GROW_TEMPLATES["grow/strain/form"]

    def get_context_data(self, **kwargs):
        context = kwargs
        context.setdefault('breeder', self.breeder)
        context.setdefault('form', StrainForm())
        context.setdefault('strain', None)
        context.setdefault('form_template', self.form_template)
        return context

    def get(self, request: HttpRequest, breeder_pk: int) -> HttpResponse:
        self.breeder = get_object_or_404(Breeder, pk=breeder_pk)
        self.strain = None

        return render(request, self.template_name, self.get_context_data())

    def post(self, request: HttpRequest, breeder_pk: int) -> HttpResponse:
        self.breeder = get_object_or_404(Breeder, pk=breeder_pk)
        self.strain = None
        form = StrainForm(request.POST, request.FILES)

        if form.is_valid():
            self.strain = form.save(commit=False)
            if form.cleaned_data['flowering_time_unit'] == 'w':
                self.strain.flowering_time_days = self.strain.flowering_time_days * 7
            self.strain.created_by = self.request.user
            self.strain.breeder = self.breeder
            self.strain.save()

            return redirect(reverse("grow:strain-detail", kwargs={
                'breeder_slug': self.strain.breeder.slug,
                'slug': self.strain.slug,
            }))

        return render(request, self.template_name,
                      context=self.get_context_data(form=form,
                                                    strain=self.strain))


class StrainUpdateView(LoginRequiredMixin, View):
    template_name = settings.GROW_TEMPLATES["grow/strain/strain/update"]
    form_template_name = settings.GROW_TEMPLATES["grow/strain/form"]

    def get_context_data(self, **kwargs):
        context = kwargs
        context.setdefault('breeder', self.breeder)
        context.setdefault('form', StrainForm(instance=self.strain))
        context.setdefault('strain', self.strain)
        context.setdefault('form_template', self.form_template_name)
        return context

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.strain = get_object_or_404(Strain, pk=pk)
        self.breeder = self.strain.breeder
        return render(request, self.template_name, context=self.get_context_data())

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.strain = get_object_or_404(Strain, pk=pk)

        form = StrainForm(request.POST, request.FILES, instance=self.strain)

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

        return render(request, self.template_name, self.get_context_data(form=form))


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
                logger.error("Unable to delete strain %s! (%s)", self.strain.name, str(ex))
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
                logger.error("Unable to delete strain %s! (%s)", self.strain.name, str(ex))
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
        year = int(form.cleaned_data['purchased_on_year'])
        month = int(form.cleaned_data['purchased_on_month'])
        day = int(form.cleaned_data['purchased_on_day'])

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
            return self.form_valid(form)
        else:
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

        if self.feminized:
            self.strain.remove_feminized_seeds_from_stock(
                self.request.user,
                form.cleaned_data['quantity']
            )
        else:
            self.strain.remove_regular_seeds_from_stock(
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

        return render(request, self.template_name, context={
            'strain': strain,
            'form': form,
        })


class StrainTranslationView(LoginRequiredMixin, View):
    template_name = settings.GROW_TEMPLATES['grow/strain/strain/translation']

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        strain = get_object_or_404(Strain, pk=pk)

        lang_code = get_language()
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
        return super(StrainAddToStock2View, self).form_valid(form)

    def form_invalid(self, form):
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
        try:
            strain = Strain.objects.get(pk=int(form.cleaned_data['strain'])
                                        if form.cleaned_data['strain'] else 0)
        except Strain.DoesNotExist:
            strain = None
            raise Http404("Strain not found!")

        if strain:
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

        self.instance = form.save(commit=False)
        self.instance.user = self.request.user
        return super(StrainUpdateStockView, self).form_valid(form)

    def form_invalid(self, form):
        super(StrainUpdateStockView, self).form_invalid(form)
        return render(self.request, self.success_template_name,
                      context=self.get_context_data(form=form))


class SeedsInStockInfoPaginator(QuerySetPaginator):
    urlvars = {'page': 'sis_p', 'paginate_by': 'sis_pgn'}


class HxSeedsInStockInfoView(LoginRequiredMixin, BaseView):
    template_name = settings.GROW_TEMPLATES['grow/seeds_in_stock/hx/info']
    logger = logging.getLogger(f"{__name__}.HxSeedsInStockInfoView")

    def get_context_data(self, **kwargs):
        seeds_in_stock = StrainsInStock.objects.filter(
            user=self.request.user,
            quantity__gt=0
        )

        render_table = self.request.GET.get('render_table', '1') == '1'
        render_text = self.request.GET.get('render_text', '0') == '1'
        render_user_text = self.request.GET.get('render_user_text', '0') == '1'

        sis = self.request.user.seeds_in_stock.filter(quantity__gt=0)
        n_seeds_in_stock = sis.aggregate(total=Sum('quantity'))['total'] or 0

        n_feminized_seeds_in_stock = sis.filter(
            is_feminized=True
        ).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        n_regular_seeds_in_stock = sis.filter(
            is_feminized=False
        ).aggregate(
            total=Sum('quantity')
        )['total'] or 0

        n_autoflowering_seeds_in_stock = sis.filter(
            strain__is_automatic=True
        ).aggregate(total=Sum('quantity'))['total'] or 0

        n_photoperiod_seeds_in_stock = sis.filter(
            strain__is_automatic=False
        ).aggregate(total=Sum('quantity'))['total'] or 0

        try:
            paginate_by = int(self.request.GET.get(
                'seeds_in_stock_paginate_by',
                self.request.GET.get(
                    'sis_paginate_by',
                    self.request.GET.get(
                        'sis_pgn',
                        self.request.GET.get(
                            'paginate_by',
                            self.request.GET.get(
                                'pgn',
                                settings.GROW_USER_SETTINGS(self.request).paginate
                            )
                        )
                    )
                )
            ))
        except (TypeError, ValueError):
            paginate_by = settings.GROW_USER_SETTINGS(self.request).paginate

        if n_seeds_in_stock == 0:
            n_pages = 1
        else:
            n_pages = (n_seeds_in_stock + paginate_by - 1) // paginate_by

        try:
            page = int(self.request.GET.get(
                'seeds_in_stock_page',
                self.request.GET.get(
                    'sis_page',
                    self.request.GET.get(
                        'sis_p',
                        self.request.GET.get(
                            'page',
                            self.request.GET.get('p', 1)
                        )
                    )
                )
            ))
        except (TypeError, ValueError) as ex:
            logger.error(f"Error parsing page number: {ex}")
            page = 1

        page = max(1, min(page, n_pages))

        sort = self.request.GET.get(
            'sis_sort',
            self.request.GET.get(
                'sis_s',
                self.request.GET.get(
                    'sort',
                    self.request.GET.get('s', 'strain')
                )
            )
        )
        ordering = self.request.GET.get(
            'sis_ordering',
            self.request.GET.get(
                'sis_ord',
                self.request.GET.get(
                    'sis_o',
                    self.request.GET.get(
                        'ordering',
                        self.request.GET.get(
                            'ord',
                            self.request.GET.get('o', 'asc')
                        )
                    )
                )
            )
        )
        if ordering in ['asc', 'a', 'ascending', 'up', '1']:
            ordering = 'asc'
        elif ordering in ['desc', 'd', 'descending', 'down', '-1']:
            ordering = 'desc'
        else:
            self.logger.warning(f"Invalid ordering value: {ordering}. Defaulting to 'asc'.")
            ordering = 'asc'

        if sort == 'strain':
            if ordering == 'asc':
                seeds_in_stock = seeds_in_stock.order_by(
                    'strain__name', 'strain__breeder__name', 'is_feminized')
            else:
                seeds_in_stock = seeds_in_stock.order_by(
                    '-strain__name', '-strain__breeder__name', '-is_feminized')
        elif sort == 'breeder':
            if ordering == 'asc':
                seeds_in_stock = seeds_in_stock.order_by(
                    'strain__breeder__name', 'strain__name', 'is_feminized')
            else:
                seeds_in_stock = seeds_in_stock.order_by(
                    '-strain__breeder__name', '-strain__name', '-is_feminized')
        elif sort == 'genotype':
            if ordering == 'asc':
                seeds_in_stock = seeds_in_stock.order_by(
                    'strain__genotype_data',
                    'strain__name',
                    'strain__breeder__name',
                    'is_feminized')  # noqa: E501
            else:
                seeds_in_stock = seeds_in_stock.order_by(
                    '-strain__genotype_data',
                    'strain__name',
                    'strain__breeder__name',
                    'is_feminized')  # noqa: E501
        elif sort == 'purchased_on':
            if ordering == 'asc':
                seeds_in_stock = seeds_in_stock.order_by(
                    'purchased_on',
                    'strain__name',
                    'strain__breeder__name',
                    'is_feminized')  # noqa: E501
            else:
                seeds_in_stock = seeds_in_stock.order_by(
                    '-purchased_on',
                    'strain__name',
                    'strain__breeder__name',
                    'is_feminized')  # noqa: E501
        elif sort == 'quantity':
            if ordering == 'asc':
                seeds_in_stock = seeds_in_stock.order_by(
                    'quantity',
                    'strain__name',
                    'strain__breeder__name',
                    'is_feminized')
            else:
                seeds_in_stock = seeds_in_stock.order_by(
                    '-quantity',
                    'strain__name',
                    'strain__breeder__name',
                    'is_feminized')
        elif sort == 'type':
            if ordering == 'asc':
                seeds_in_stock = seeds_in_stock.order_by(
                    'is_feminized',
                    'strain__name',
                    'strain__breeder__name')
            else:
                seeds_in_stock = seeds_in_stock.order_by(
                    '-is_feminized',
                    'strain__name',
                    'strain__breeder__name')
        elif sort == 'genotype':
            if ordering == 'asc':
                seeds_in_stock = seeds_in_stock.order_by(
                    'strain__genotype',
                    'strain__name',
                    'strain__breeder__name',
                    'is_feminized')  # noqa: E501
            else:
                seeds_in_stock = seeds_in_stock.order_by(
                    '-strain__genotype',
                    'strain__name',
                    'strain__breeder__name',
                    'is_feminized')  # noqa: E501
        elif sort in ['flt', 'flowering', 'flowering_time']:
            sort = 'flowering_time'
            if ordering == 'asc':
                seeds_in_stock = seeds_in_stock.order_by(
                    'strain__flowering_time_days',
                    'strain__name',
                    'strain__breeder__name',
                    'is_feminized')  # noqa: E501
            else:
                seeds_in_stock = seeds_in_stock.order_by(
                    '-strain__flowering_time_days',
                    'strain__name',
                    'strain__breeder__name',
                    'is_feminized')
        else:
            self.logger.warning(f"Invalid sort value: {sort}. Defaulting to 'strain'.")
            sort = 'strain'
            ordering = 'asc'
            seeds_in_stock = seeds_in_stock.order_by(
                'strain__name',
                'strain__breeder__name',
                'is_feminized')

        paginator = SeedsInStockInfoPaginator(
            seeds_in_stock,
            url_path='grow:hx-seeds-in-stock-info',
            url_variables={
                'render_table': '1' if render_table else '0',
                'render_text': '1' if render_text else '0',
                'render_user_text': '1' if render_user_text else '0',
                'sis_sort': sort,
                'sis_ord': ordering,
            },
            paginate_by=paginate_by,
            page=page)

        context = {
            'n_strains_in_stock': StrainsInStock.objects.filter(user=self.request.user).count(),
            'n_seeds_in_stock': n_seeds_in_stock,
            'n_feminized_seeds_in_stock': n_feminized_seeds_in_stock,
            'n_regular_seeds_in_stock': n_regular_seeds_in_stock,
            'n_autoflowering_seeds_in_stock': n_autoflowering_seeds_in_stock,
            'n_photoperiod_seeds_in_stock': n_photoperiod_seeds_in_stock,
            'seeds_in_stock_render_table': render_table,
            'seeds_in_stock_render_text': render_text,
            'seeds_in_stock_render_user_text': render_user_text,
            'seeds_in_stock_current_page': page,
            'seeds_in_stock_paginator': paginator,
            'seeds_in_stock_scroll_to_card': True,
            'seeds_in_stock_user': kwargs.get('seeds_in_stock_user', self.request.user),
            'seeds_in_stock_sort': sort,
            'seeds_in_stock_ordering': ordering,
            'seeds_in_stock_update_page_url': True,
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


class HxMySeedsInStockView(LoginRequiredMixin, View):
    template_name = settings.GROW_TEMPLATES['grow/seeds_in_stock/hx/my_seeds_in_stock']
    update_page_url = True
    logger = logging.getLogger(f"{__name__}.HxMySeedsInStockView")
    urlvars = {
        'sis_sort': 'sis_sort',
        'sis_ordering': 'sis_ord',
    }
    sis_hx_target = "#my-seeds-in-stock"

    def get_context_data(self, **kwargs):
        context = kwargs
        seeds_in_stock = StrainsInStock.objects.filter(
            user=self.request.user,
            quantity__gt=0
        )
        sort = self.request.GET.get(
            'sis_sort',
            self.request.GET.get(
                'sis_s',
                self.request.GET.get(
                    'sort',
                    self.request.GET.get(
                        's',
                        context.get('sis_sort', 'strain')
                    )
                )
            )
        )
        ordering = self.request.GET.get(
            'sis_ordering',
            self.request.GET.get(
                'sis_ord',
                self.request.GET.get(
                    'sis_o',
                    self.request.GET.get(
                        'ordering',
                        self.request.GET.get(
                            'ord',
                            context.get('sis_ordering', 'asc')
                        )
                    )
                )
            )
        )
        if ordering in ['asc', 'a', 'ascending', 'up', '1']:
            ordering = 'asc'
        elif ordering in ['desc', 'd', 'descending', 'down', '-1']:
            ordering = 'desc'
        else:
            self.logger.warning(f"Invalid ordering value: {ordering}. Defaulting to 'asc'.")
            ordering = 'asc'

        if sort == 'strain':
            if ordering == 'asc':
                seeds_in_stock = seeds_in_stock.order_by(
                    'strain__name', 'strain__breeder__name', 'is_feminized')
            else:
                seeds_in_stock = seeds_in_stock.order_by(
                    '-strain__name', '-strain__breeder__name', '-is_feminized')
        elif sort == 'breeder':
            if ordering == 'asc':
                seeds_in_stock = seeds_in_stock.order_by(
                    'strain__breeder__name', 'strain__name', 'is_feminized')
            else:
                seeds_in_stock = seeds_in_stock.order_by(
                    '-strain__breeder__name', '-strain__name', '-is_feminized')
        elif sort == 'genotype':
            if ordering == 'asc':
                seeds_in_stock = seeds_in_stock.order_by(
                    'strain__genotype_data',
                    'strain__name',
                    'strain__breeder__name',
                    'is_feminized')
            else:
                seeds_in_stock = seeds_in_stock.order_by(
                    '-strain__genotype_data',
                    'strain__name',
                    'strain__breeder__name',
                    'is_feminized')
        elif sort == 'purchased_on':
            if ordering == 'asc':
                seeds_in_stock = seeds_in_stock.order_by(
                    'purchased_on',
                    'strain__name',
                    'strain__breeder__name',
                    'is_feminized')
            else:
                seeds_in_stock = seeds_in_stock.order_by(
                    '-purchased_on',
                    'strain__name',
                    'strain__breeder__name',
                    'is_feminized')
        elif sort == 'quantity':
            if ordering == 'asc':
                seeds_in_stock = seeds_in_stock.order_by(
                    'quantity',
                    'strain__name',
                    'strain__breeder__name',
                    'is_feminized')
            else:
                seeds_in_stock = seeds_in_stock.order_by(
                    '-quantity',
                    'strain__name',
                    'strain__breeder__name',
                    'is_feminized')
        elif sort in ['flowering_time', 'flt', 'floweringtime', 'flowering']:
            sort = 'flowering_time'
            if ordering == 'asc':
                seeds_in_stock = seeds_in_stock.order_by(
                    'strain__flowering_time_days',
                    'strain__name',
                    'strain__breeder__name',
                    'is_feminized')
            else:
                seeds_in_stock = seeds_in_stock.order_by(
                    '-strain__flowering_time_days',
                    'strain__name',
                    'strain__breeder__name',
                    'is_feminized')
        elif sort == 'growlogs':
            if ordering == 'asc':
                seeds_in_stock = seeds_in_stock.annotate(
                    growlogs_count=Count(
                        'strain__growlog_strains__growlog',
                        filter=Q(strain__growlog_strains__growlog__grower=self.request.user)
                    )
                ).order_by(
                    'growlogs_count',
                    'strain__name',
                    'strain__breeder__name',
                    'is_feminized'
                )
            else:
                seeds_in_stock = seeds_in_stock.annotate(
                    growlogs_count=Count(
                        'strain__growlog_strains__growlog',
                        filter=Q(strain__growlog_strains__growlog__grower=self.request.user)
                    )
                ).order_by(
                    '-growlogs_count',
                    'strain__name',
                    'strain__breeder__name',
                    'is_feminized'
                )
        else:
            self.logger.warning(f"Invalid sort value: {sort}. Defaulting to 'strain'.")
            sort = 'strain'
            ordering = 'asc'
            seeds_in_stock = seeds_in_stock.order_by(
                'strain__name',
                'strain__breeder__name',
                'is_feminized')

        if self.urlvars != HxMySeedsInStockView.urlvars:
            self.urlvars.setdefault('sis_sort',
                                    HxMySeedsInStockView.urlvars.get('sis_sort', 'sis_sort'))
            self.urlvars.setdefault('sis_ordering',
                                    HxMySeedsInStockView.urlvars.get('sis_ordering', 'sis_ord'))

        context['seeds_in_stock'] = seeds_in_stock
        context['urlvars'] = self.urlvars
        context['sis_sort'] = sort
        context['sis_ordering'] = ordering
        context['hx_target'] = self.sis_hx_target
        context.setdefault('seeds_in_stock_update_page_url', self.update_page_url)
        context.setdefault('update_page_url', self.update_page_url)

        return context

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name, self.get_context_data())


class MySeedsInStockView(HxMySeedsInStockView):
    template_name = settings.GROW_TEMPLATES['grow/seeds_in_stock/my_seeds_in_stock']
    update_page_url = False
    urlvars = {
        'sis_sort': 'sort',
        'sis_ordering': 'ord',
    }

    def get_context_data(self, **kwargs):
        return HxMySeedsInStockView.get_context_data(self, **kwargs)

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name, self.get_context_data())
