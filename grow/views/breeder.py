from ._base import BaseView
from grow import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import FormView, UpdateView
from grow.forms import DeleteWithSlugForm
from django.http import Http404, HttpRequest, HttpResponse
from django.utils.safestring import mark_safe
from django.utils.translation import get_language
from grow.growapi.models import Breeder, Strain
from grow.forms import BreederFilterForm, StrainSearchForm, StrainFilterForm, BreederTranslationForm
from django.db.models.functions import Lower
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.db.models import Count
from django.urls import reverse, reverse_lazy
import logging
import re


logger = logging.getLogger(__name__)


class BreederIndexView(BaseView):
    template_name = settings.GROW_TEMPLATES['grow/breeder']

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

        group_breeders = (breeders.count() > 10 or not search_query)
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


class HxBreederStrainsView(BaseView):
    template_name = settings.GROW_TEMPLATES['grow/breeder/hx/strains']

    def get_context_data(self, **kwargs):
        context = kwargs
        if hasattr(self, 'strains'):
            strains = self.strains
        else:
            strains = self.breeder.strains.all()

        filter = getattr(
            self,
            'filter',
            self.request.GET.get(
                'strains_filter',
                self.request.GET.get(
                    'filter',
                    self.request.GET.get('f', "")
                )
            )
        ).strip()

        if filter:
            strains = strains.filter(name__icontains=filter)

        sort = self.request.GET.get(
            'strains_sort',
            self.request.GET.get(
                'sort',
                self.request.GET.get('s', 'name')
            )
        )

        ordering = self.request.GET.get(
            'strains_order',
            self.request.GET.get(
                'order',
                self.request.GET.get('o', 'asc')
            )
        )

        if ordering in ['asc', 'ascending', 'a', '1']:
            ordering = 'asc'
        elif ordering in ['desc', 'descending', 'd', '0']:
            ordering = 'desc'
        else:
            ordering = 'asc'

        if sort == 'name':
            if ordering == 'asc':
                strains = strains.order_by(Lower("name"))
            elif ordering == 'desc':
                strains = strains.order_by(Lower("name").desc())
        elif sort == 'genotype':
            if ordering == 'asc':
                strains = strains.order_by("genotype_data")
            elif ordering == 'desc':
                strains = strains.order_by("-genotype_data")
        elif sort == 'flowering' or sort == 'flowering_time':
            if ordering == 'asc':
                strains = strains.order_by("flowering_time_days")
            elif ordering == 'desc':
                strains = strains.order_by("-flowering_time_days")
        elif sort == 'growlogs' or sort == 'growlog_count':
            if ordering == 'asc':
                strains = strains.annotate(
                    growlog_strains_count=Count('growlog_strains')
                ).order_by("growlog_strains_count")
            elif ordering == 'desc':
                strains = strains.annotate(
                    growlog_strains_count=Count('growlog_strains')
                ).order_by("-growlog_strains_count")
        else:
            sort = 'name'
            if ordering == 'asc':
                strains = strains.order_by(Lower("name"))
            elif ordering == 'desc':
                strains = strains.order_by(Lower("name").desc())

        strains_allowed_to_edit = []
        for strain in strains:
            strain.allowed_to_edit = False
            strain.allowed_to_delete = False

            if self.request.user.is_authenticated:
                if self.request.user.is_staff or self.request.user.is_superuser:
                    strains_allowed_to_edit.append(strain.id)
                elif self.request.user.id == self.breeder.created_by.id:
                    strains_allowed_to_edit.append(strain.id)
                elif self.request.user.groups.filter(name='grow-breeder-editors').exists():
                    strains_allowed_to_edit.append(strain.id)

        strains_allowed_to_delete = []
        for strain in strains:
            if strain.growlog_count == 0 and self.request.user.is_authenticated:
                if self.request.user.is_staff or self.request.user.is_superuser:
                    strains_allowed_to_delete.append(strain.id)
                elif self.breeder.created_by and self.request.user.id == self.breeder.created_by.id:
                    strains_allowed_to_delete.append(strain.id)
                elif self.request.user.groups.filter(name='grow-breeder-editors').exists():
                    strains_allowed_to_delete.append(strain.id)

        allowed_to_add_strains = False
        if self.request.user.is_authenticated:
            if self.request.user.is_staff or self.request.user.is_superuser:
                allowed_to_add_strains = True
            elif self.breeder.created_byself.request.user.id == self.breeder.created_by.id:
                allowed_to_add_strains = True
            elif self.request.user.groups.filter(name='grow-breeder-editors').exists():
                allowed_to_add_strains = True
            elif self.request.user.groups.filter(name='grow-strain-creators').exists():
                allowed_to_add_strains = True
            elif (
                not self.breeder.created_by
                and self.request.user.groups.filter(name='grow-user').exists()
            ):
                allowed_to_add_strains = True

        context.setdefault('breeder', self.breeder)
        context.setdefault('strains_allowed_to_edit', strains_allowed_to_edit)
        context.setdefault('strains_allowed_to_delete', strains_allowed_to_delete)
        context.setdefault('strains', strains)
        context.setdefault('strains_filter', filter)
        context.setdefault('strains_sort', sort)
        context.setdefault('strains_order', ordering)
        context.setdefault('allowed_to_add_strains', allowed_to_add_strains)

        return context

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.breeder = get_object_or_404(Breeder, pk=pk)
        return render(request, self.template_name, context=self.get_context_data())


class BreederView(HxBreederStrainsView):
    template_name = settings.GROW_TEMPLATES['grow/breeder/detail']

    def get_context_data(self, **kwargs):
        context: dict = HxBreederStrainsView.get_context_data(self, **kwargs)

        language = get_language()

        translation = self.breeder.get_translation(language)

        allowed_to_edit = False
        if self.request.user.is_authenticated:
            if self.request.user.is_staff or self.request.user.is_superuser:
                allowed_to_edit = True
            elif self.request.user.id == self.breeder.created_by.id:
                allowed_to_edit = True
            elif self.request.user.groups.filter(name='grow-breeder-editors').exists():
                allowed_to_edit = True

        allowed_to_delete = False
        if self.breeder.growlog_count == 0 and self.request.user.is_authenticated:
            if self.request.user.is_staff or self.request.user.is_superuser:
                allowed_to_delete = True
            elif self.request.user.id == self.breeder.created_by.id:
                allowed_to_delete = True
            elif self.request.user.groups.filter(name='grow-breeder-editors').exists():
                allowed_to_delete = True

        allowed_to_translate = False
        if self.request.user.is_authenticated:
            if self.request.user.is_staff or self.request.user.is_superuser:
                allowed_to_translate = True
            elif self.request.user.id == self.breeder.created_by.id:
                allowed_to_translate = True
            elif self.request.user.groups.filter(name='grow-breeder-editors').exists():
                allowed_to_translate = True
            elif self.request.user.groups.filter(name='grow-translators').exists():
                allowed_to_translate = True

        allowed_to_add_strains = False
        if self.request.user.is_authenticated:
            if self.request.user.is_staff or self.request.user.is_superuser:
                allowed_to_add_strains = True
            elif self.request.user.id == self.breeder.created_by.id:
                allowed_to_add_strains = True
            elif self.request.user.groups.filter(name='grow-breeder-editors').exists():
                allowed_to_add_strains = True
            elif self.request.user.groups.filter(name='grow-strain-creators').exists():
                allowed_to_add_strains = True

        filter_strains_form = StrainFilterForm()

        if translation and translation.seedfinder_url:
            seedfinder_url = translation.seedfinder_url
        else:
            seedfinder_url = self.breeder.seedfinder_url

        if translation and translation.breeder_url:
            breeder_url = translation.breeder_url
        else:
            breeder_url = self.breeder.breeder_url

        context.setdefault('allowed_to_edit', allowed_to_edit)
        context.setdefault('allowed_to_delete', allowed_to_delete)
        context.setdefault('allowed_to_translate', allowed_to_translate)
        context.setdefault('allowed_to_add_strains', allowed_to_add_strains)
        context.setdefault('translation', translation)
        context.setdefault('filter_strains_form', filter_strains_form)
        context.setdefault('seedfinder_url', seedfinder_url)
        context.setdefault('breeder_url', breeder_url)

        return context

    def get(self, request: HttpRequest, slug: str) -> HttpResponse:
        self.breeder = get_object_or_404(Breeder, slug=slug)
        return render(request, self.template_name, context=self.get_context_data())


class BreederCreateView(LoginRequiredMixin, CreateView):
    template_name = settings.GROW_TEMPLATES['grow/breeder/create']
    form_template_name = settings.GROW_TEMPLATES['grow/breeder/form']
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form_template' not in context:
            context['form_template'] = self.form_template_name
        return context

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
    form_template_name = settings.GROW_TEMPLATES['grow/breeder/form']

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form_template' not in context:
            context['form_template'] = self.form_template_name
        return context

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

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        breeder = get_object_or_404(Breeder, pk=pk)
        return render(request, self.template_name, context={
            'form': self.form_class(),
            'breeder': breeder,
        })

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        breeder = get_object_or_404(Breeder, pk=pk)
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
                logger.error("Deleting breeder \"%s\" failed! (%s)", self.breeder.name, str(ex))
        return redirect(self.get_failed_url())

    def form_invalid(self, form):
        return redirect(self.get_failed_url())


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
            pass

        return render(request, self.template_name, context={
            'breeder': breeder,
            'form': form,
        })


class HxBreederTranslationView(LoginRequiredMixin, View):
    template_name = settings.GROW_TEMPLATES['grow/breeder/hx/translation']

    def get(self, request: HttpRequest, pk: int, language_code: str) -> HttpResponse:
        breeder = get_object_or_404(Breeder, pk=pk)
        if not (re.match(r'^[a-z]{2}(-[a-z]{2})?$', language_code)):
            raise Http404("Invalid language code format!")

        existing_translation = breeder.translations.filter(language_code=language_code).first()

        if existing_translation:
            form = BreederTranslationForm(instance=existing_translation)
        else:
            short_lang_code = language_code.split('-')[0]

            seedfinder_url = breeder.seedfinder_url

            if short_lang_code in ['de', 'fr', 'es', 'en']:
                if breeder.seedfinder_url:
                    seedfinder_url = re.sub('(/en/|/de/|/fr/|/es/)',
                                            f'/{short_lang_code}/',
                                            breeder.seedfinder_url)

                form = BreederTranslationForm(initial={
                    'language_code': language_code,
                    'name': breeder.name,
                    'breeder_url': breeder.breeder_url,
                    'seedfinder_url': seedfinder_url
                })

        return render(request, self.template_name, context={
            'breeder': breeder,
            'form': form,
        })


class HxBreederStrainFilterView(HxBreederStrainsView):
    template_name = settings.GROW_TEMPLATES['grow/breeder/hx/strains']

    def post(self, request: HttpRequest, breeder_pk: int) -> HttpResponse:
        form = StrainFilterForm(request.POST)
        if form.is_valid():
            self.filter = form.cleaned_data['search_query'].strip()
        else:
            self.filter = None

        if not self.filter:
            delattr(self, 'filter')

        self.breeder = get_object_or_404(Breeder, pk=breeder_pk)

        return render(request, self.template_name, context=self.get_context_data())
