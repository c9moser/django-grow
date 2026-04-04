from ._base import BaseView
from grow import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import FormView, UpdateView
from grow.forms import DeleteWithSlugForm
from django.http import Http404, HttpRequest, HttpResponse
from django.utils.safestring import mark_safe
from django.utils.translation import get_language, activate
from grow.growapi.models import Breeder, Strain
from grow.forms import BreederFilterForm, StrainSearchForm, StrainFilterForm, BreederTranslationForm
from django.conf import settings as django_settings
from django.db.models.functions import Lower
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
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
