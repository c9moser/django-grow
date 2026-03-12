from typing import Any
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from django.http import HttpRequest, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView, FormView
from django.db.models import Count
from grow.forms.growlog import (
    GrowlogAddStrainForm,
    GrowlogForm,
    GrowlogDescriptionForm,
    GrowlogNotesForm,
    GrowlogQuantityForm,
    GrowlogSeedsFromStockForm,
    GrowlogStrainDeleteForm,
)
from grow.growapi.models.strain import Strain
from ..growapi.models import (
    Growlog,
    GrowlogEntry,
    # GrowlogEntryImage,
    GrowlogStrain,
    Breeder,
    # Strain,

)
# from django.urls import reverse

from ..settings import GROW_TEMPLATES, GROW_USER_SETTINGS
from ._base import BaseView
from ..growapi.permission import (
    growlog_user_is_allowed_to_view,
    growlog_user_is_allowed_to_edit,
)


class GrowlogDetailView(BaseView):
    template_name = GROW_TEMPLATES['grow/growlog/detail']
    strains_template_name = GROW_TEMPLATES['grow/growlog/hx-growlog-strains']
    entries_template_name = GROW_TEMPLATES['grow/growlog/hx-growlog-entries']

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        growlog = get_object_or_404(Growlog, pk=pk)
        if not growlog_user_is_allowed_to_view(request.user, growlog):
            return HttpResponse(status=403)
        growlog_strains = GrowlogStrain.objects.filter(growlog=growlog).order_by(
            'strain__name', 'strain__breeder__name')
        entries = GrowlogEntry.objects.filter(growlog=growlog).order_by('-timestamp')
        context = {
            'growlog': growlog,
            'growlog_strains': growlog_strains,
            'entries': entries,
            'can_edit': growlog_user_is_allowed_to_edit(request.user, growlog),
            'strains_template': self.strains_template_name,
            'entries_template': self.entries_template_name,
            'notes_template': GROW_TEMPLATES['grow/growlog/hx-growlog-notes'],
            'description_template': GROW_TEMPLATES['grow/growlog/hx-growlog-description'],
        }
        return render(request, self.template_name, context)


class GrowlogCreateView(LoginRequiredMixin, CreateView):
    model = Growlog
    form_class = GrowlogForm
    template_name = GROW_TEMPLATES['grow/growlog/create']
    parent_template_name = GROW_TEMPLATES['grow/growlog/form']

    def get_success_url(self) -> str:
        return reverse('grow:growlog-detail', kwargs={'pk': self.instance.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['parent_template'] = self.parent_template_name
        return context

    def form_valid(self, form):
        growlog: Growlog = form.save(commit=False)
        growlog.grower = self.request.user
        growlog.save()
        self.instance = growlog
        return super().form_valid(form)


class GrowlogUpdateView(LoginRequiredMixin, UpdateView):
    model = Growlog
    form_class = GrowlogForm
    template_name = GROW_TEMPLATES['grow/growlog/update']
    parent_template_name = GROW_TEMPLATES['grow/growlog/form']

    def get_success_url(self) -> str:
        return reverse('grow:growlog-detail', kwargs={'pk': self.instance.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['parent_template'] = self.parent_template_name
        return context


class GrowlogDeleteView(LoginRequiredMixin, DeleteView):
    model = Growlog
    template_name = GROW_TEMPLATES['grow/growlog/delete']

    def get_success_url(self) -> str:
        return reverse('grow:user-info')

    def post(self, request: HttpRequest, pk, **kwargs) -> HttpResponse:
        growlog = get_object_or_404(Growlog, pk=pk)  # check if growlog exists
        if growlog.grower != request.user:
            return HttpResponse(status=403)  # forbid deletion if user is not the grower
        return super().post(request, pk=pk, **kwargs)


class HxGrowlogStrainsInfoView(BaseView):
    template_name = GROW_TEMPLATES['grow/growlog/hx-growlog-strains']

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = kwargs
        context["growlog"] = self.growlog
        context["growlog_strains"] = GrowlogStrain.objects.filter(growlog=self.growlog).order_by(
            'strain__name', 'strain__breeder__name')
        context["can_edit"] = growlog_user_is_allowed_to_edit(self.request.user, self.growlog)
        return context

    def get(self, request: HttpRequest, growlog_pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=growlog_pk)
        if not self.growlog.is_user_allowed_to_view(request.user):
            return HttpResponse(status=403)

        return render(request, self.template_name, self.get_context_data())


class HxGrowlogAddSeedsView(LoginRequiredMixin, HxGrowlogStrainsInfoView, FormView):
    template_name = GROW_TEMPLATES['grow/growlog/hx-growlog-seeds_add']
    info_template_name = GROW_TEMPLATES['grow/growlog/hx-growlog-strains']
    form_class = GrowlogSeedsFromStockForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        return FormView.get_context_data(
            self,
            **HxGrowlogStrainsInfoView.get_context_data(self, **kwargs)
        )

    def get(self, request, growlog_pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=growlog_pk)
        if self.growlog.grower != request.user:
            return HttpResponse(status=403)

        form = GrowlogSeedsFromStockForm(user=request.user)
        return render(request, self.template_name, {
            'form': form,
            'growlog': self.growlog,
        })

    def form_valid(self, form):
        sis = form.cleaned_data['seeds_in_stock']
        if sis.quantity > 0:
            if sis.quantity - form.cleaned_data['quantity'] < 0:
                quantity = sis.quantity
            else:
                quantity = form.cleaned_data['quantity']
                sis.quantity -= quantity

            if sis.quantity == 0:
                sis.purchased_on = None
                sis.notes = None
            sis.save()

        try:
            gls: GrowlogStrain = self.growlog.growlog_strains.get(strain=sis.strain)
            gls.quantity += quantity
            gls.is_grown_from_seed = True
            gls.save()
        except GrowlogStrain.DoesNotExist:
            gls = GrowlogStrain.objects.create(
                growlog=self.growlog,
                strain=sis.strain,
                is_grown_from_seed=True,
                quantity=quantity
            )

        return render(self.request, self.info_template_name, self.get_context_data(
            strain=sis.strain,
            is_grown_from_seed=True,
            quantity=quantity,
        ))

    def form_invalid(self, form):
        return render(self.request, self.info_template_name, self.get_context_data(
            form=form,
        ))

    def post(self, request: HttpRequest, growlog_pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=growlog_pk)
        if self.growlog.grower != request.user:
            return HttpResponse(status=403)

        form = GrowlogSeedsFromStockForm(request.POST, user=request.user)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class HxGrowlogAddPlantsView(LoginRequiredMixin, HxGrowlogStrainsInfoView, FormView):
    template_name = GROW_TEMPLATES['grow/growlog/hx-growlog-plants_add']
    result_template_name = GROW_TEMPLATES['grow/growlog/hx-growlog-strains']
    form_class = GrowlogQuantityForm

    def get_context_data(self, **kwargs):
        return FormView.get_context_data(
            self,
            **HxGrowlogStrainsInfoView.get_context_data(self, **kwargs)
        )

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.growlog_strain = get_object_or_404(GrowlogStrain, pk=pk)
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog_strain.growlog):
            return HttpResponse(status=403)

        return render(request, self.template_name, {
            'form': self.form_class(),
            'growlog': self.growlog_strain.growlog,
            'growlog_strain': self.growlog_strain,
            'strain': self.growlog_strain.strain,
        })

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.growlog_strain = get_object_or_404(GrowlogStrain, pk=pk)
        self.growlog = self.growlog_strain.growlog

        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            return HttpResponse(status=403)

        form = self.form_class(request.POST)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        if (self.growlog_strain.quantity + form.cleaned_data['quantity']) < 0:
            self.growlog_strain.quantity = 0
        else:
            self.growlog_strain.quantity += form.cleaned_data['quantity']
        self.growlog_strain.save()

        return render(self.request, self.result_template_name, self.get_context_data(
            strain=self.growlog_strain.strain,
            growlog_strain=self.growlog_strain,
            growlog=self.growlog_strain.growlog,
            is_grown_from_seed=self.growlog_strain.is_grown_from_seed,
            quantity=form.cleaned_data['quantity'],
        ))

    def form_invalid(self, form):
        return render(self.request, self.result_template_name, self.get_context_data(
            form=form,
            strain=self.growlog_strain.strain,
            growlog_strain=self.growlog_strain,
            growlog=self.growlog_strain.growlog,
        ))


class HxGrowlogRemovePlantsView(LoginRequiredMixin, HxGrowlogStrainsInfoView, FormView):
    template_name = GROW_TEMPLATES['grow/growlog/hx-growlog-plants_remove']
    result_template_name = GROW_TEMPLATES['grow/growlog/hx-growlog-strains']
    form_class = GrowlogQuantityForm

    def get_context_data(self, **kwargs):
        return FormView.get_context_data(
            self,
            **HxGrowlogStrainsInfoView.get_context_data(self, **kwargs)
        )

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.growlog_strain = get_object_or_404(GrowlogStrain, pk=pk)
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog_strain.growlog):
            return HttpResponse(status=403)

        return render(request, self.template_name, {
            'form': self.form_class(),
            'growlog': self.growlog_strain.growlog,
            'growlog_strain': self.growlog_strain,
            'strain': self.growlog_strain.strain,
        })

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.growlog_strain = get_object_or_404(GrowlogStrain, pk=pk)
        self.growlog = self.growlog_strain.growlog

        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            return HttpResponse(status=403)

        form = self.form_class(request.POST)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        if (self.growlog_strain.quantity - form.cleaned_data['quantity']) < 0:
            self.growlog_strain.quantity = 0
        else:
            self.growlog_strain.quantity -= form.cleaned_data['quantity']
        self.growlog_strain.save()

        return render(self.request, self.result_template_name, self.get_context_data(
            strain=self.growlog_strain.strain,
            growlog_strain=self.growlog_strain,
            growlog=self.growlog_strain.growlog,
            is_grown_from_seed=self.growlog_strain.is_grown_from_seed,
            quantity=form.cleaned_data['quantity'],
        ))

    def form_invalid(self, form):
        return render(self.request, self.result_template_name, self.get_context_data(
            form=form,
            strain=self.growlog_strain.strain,
            growlog_strain=self.growlog_strain,
            growlog=self.growlog_strain.growlog,
        ))


class HxGrowlogAddStrainView(LoginRequiredMixin, HxGrowlogStrainsInfoView, FormView):
    template_name = GROW_TEMPLATES['grow/growlog/hx-growlog-strain_add']
    result_template_name = GROW_TEMPLATES['grow/growlog/hx-growlog-strains']
    form_class = GrowlogAddStrainForm

    def get_form(self, form_class=None, **form_kwargs):
        if form_class is None:
            form_class = self.get_form_class()
        form = form_class(**form_kwargs)

        breeders = Breeder.objects.annotate(
            strains_count=Count('strains')
        ).filter(strains_count__gt=0).order_by('name')
        breeder = None

        form.fields['breeder'].queryset = breeders

        for _breeder in breeders:
            if _breeder.strains_count > 0:
                breeder = _breeder
                form.fields['breeder'].initial = _breeder.id
                break

        strains = None
        strain = None
        if breeder is not None:
            strains = breeder.strains.order_by('name')
            form.fields['strain'].queryset = strains

            strain = strains.first() if strains.count() > 0 else None
            form.fields['strain'].initial = strain.id if strain else None

        form.fields['is_grown_from_seed'].initial = False

        return form

    def get_context_data(self, **kwargs):
        context = FormView.get_context_data(
            self,
            **HxGrowlogStrainsInfoView.get_context_data(self, **kwargs)
        )
        if not hasattr(self, 'breeders'):
            self.breeders = Breeder.objects.annotate(
                strains_count=Count('strains')
            ).filter(strains_count__gt=0).order_by('name')

        context['breeders'] = self.breeders

        if not hasattr(self, 'breeder'):
            self.breeder = self.breeders.first() if self.breeders.count() > 0 else None
        elif not self.breeders.filter(id=self.breeder.id):
            self.breeder = self.breeders.first() if self.breeders.count() > 0 else None

        context['breeder'] = self.breeder

        if self.breeder:
            if not hasattr(self, 'strains'):
                self.strains = self.breeder.strains.order_by('name')
            context['strains'] = self.strains

            if not hasattr(self, 'strain'):
                self.strain = self.strains.first() if self.strains.count() > 0 else None
            elif not self.strains.filter(id=self.strain.id):
                self.strain = self.strains.first() if self.strains.count() > 0 else None

            context['strain'] = self.strain

        return context

    def get(self, request: HttpRequest, growlog_pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=growlog_pk)

        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            return HttpResponse(status=403)

        return render(request, self.template_name, self.get_context_data(
            form=self.get_form(),
            growlog=self.growlog,
        ))

    def post(self, request: HttpRequest, growlog_pk: int) -> HttpResponse:
        self.growlog_strain = get_object_or_404(GrowlogStrain, pk=pk)
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog_strain.growlog):
            return HttpResponse(status=403)

        form = self.form_class(request.POST)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.growlog_strain.quantity += form.cleaned_data['quantity']
        if self.growlog_strain.quantity < 0:
            self.growlog_strain.quantity = 0
        self.growlog_strain.save()

        return render(self.request, self.result_template_name, self.get_context_data(
            strain=self.growlog_strain.strain,
            growlog_strain=self.growlog_strain,
            growlog=self.growlog_strain.growlog,
            is_grown_from_seed=self.growlog_strain.is_grown_from_seed,
            quantity=form.cleaned_data['quantity'],
        ))

    def form_invalid(self, form):
        return render(self.request, self.result_template_name, self.get_context_data(
            form=form,
            strain=self.growlog_strain.strain,
            growlog_strain=self.growlog_strain,
            growlog=self.growlog_strain.growlog,
        ))


class HxGrowlogAddStrainUpdateView(HxGrowlogAddStrainView):
    template_name = GROW_TEMPLATES['grow/growlog/hx-growlog-strain_add']

    def post(self, request: HttpRequest, growlog_pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=growlog_pk)
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            return HttpResponse(status=403)

        form = self.get_form(data=request.POST)
        initial = {}

        form.is_valid()
        breeders = Breeder.objects.annotate(
            strains_count=Count('strains')
        ).filter(strains_count__gt=0).order_by('name')
        form.fields['breeder'].queryset = breeders

        if form.cleaned_data['breeder_filter']:
            breeders = breeders.filter(name__icontains=form.cleaned_data['breeder_filter'])
            form.fields['breeder'].queryset = breeders
            initial['breeder_filter'] = form.cleaned_data['breeder_filter']

        breeder = None
        if form.cleaned_data['breeder']:
            breeder = form.cleaned_data['breeder']
            print("Breeder:", breeder)
            if not breeders.filter(id=breeder.id):
                print("Breeder not in filtered breeders")
                breeder = None

        if not breeder and breeders.count() > 0:
            breeder = breeders.first()

        strains = []
        strain = None

        if breeder:
            initial['breeder'] = breeder.id
            initial['breeder'] = breeder.id

            strains = breeder.strains.all().order_by('name')
            form.fields['strain'].queryset = strains

            strain = None

            if 'strain' in form.cleaned_data and form.cleaned_data['strain']:
                strain = form.cleaned_data['strain']
                if not breeder.strains.filter(id=strain.id):
                    strain = None

            if not strain and strains:
                strain = strains.first()

            if strain:
                print("Strain:", strain)
                initial['strain'] = strain.id

        initial['is_grown_from_seed'] = form.cleaned_data['is_grown_from_seed']
        initial['quantity'] = form.cleaned_data['quantity']
        result_form = self.get_form(data=initial)
        result_form.fields['strain'].queryset = strains
        #result_form.fields['strain'].initial = strain.id if strain else None

        return render(request, self.template_name, self.get_context_data(
            form=result_form,
            growlog=self.growlog,
        ))


class HxGrowlogDeleteStrainView(LoginRequiredMixin, HxGrowlogStrainsInfoView, FormView):
    template_name = GROW_TEMPLATES['grow/growlog/hx-growlog-strain_delete']
    info_template_name = GROW_TEMPLATES['grow/growlog/hx-growlog-strains']
    form_class = GrowlogStrainDeleteForm

    def get_context_data(self, **kwargs):
        context = HxGrowlogStrainsInfoView.get_context_data(self, **kwargs)
        context['growlog_strain'] = self.growlog_strain
        context['strain'] = self.growlog_strain.strain
        context['growlog'] = self.growlog_strain.growlog
        context['form'] = kwargs.get('form', self.form_class(instance=self.growlog_strain))
        return context

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.growlog_strain = get_object_or_404(GrowlogStrain, pk=pk)
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog_strain.growlog):
            return HttpResponse(status=403)
        self.growlog = self.growlog_strain.growlog
        self.strain = self.growlog_strain.strain

        return render(request, self.template_name, self.get_context_data())

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.growlog_strain = get_object_or_404(GrowlogStrain, pk=pk)
        self.growlog = self.growlog_strain.growlog

        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            return HttpResponse(status=403)
        self.growlog_strain.delete()

        return render(request, self.info_template_name, self.get_context_data())


class HxGrowlogEditNotesView(LoginRequiredMixin, FormView):
    template_name = GROW_TEMPLATES['grow/growlog/hx-growlog-notes_edit']
    success_template_name = GROW_TEMPLATES['grow/growlog/hx-growlog-notes']

    form_class = GrowlogNotesForm

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(instance=self.growlog, **self.get_form_kwargs())

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['growlog'] = self.growlog
        return context

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=pk)
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            return HttpResponse(status=403)

        return render(request, self.template_name, context=self.get_context_data())

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=pk)
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            return HttpResponse(status=403)

        form = GrowlogNotesForm(request.POST, instance=self.growlog)
        if form.is_valid():
            form.save(commit=True)

        return render(request, self.success_template_name, context=self.get_context_data())


class HxGrowlogEditDescriptionView(LoginRequiredMixin, FormView):
    template_name = GROW_TEMPLATES['grow/growlog/hx-growlog-description_edit']
    success_template_name = GROW_TEMPLATES['grow/growlog/hx-growlog-description']

    form_class = GrowlogDescriptionForm

    def get_form(self, form_class=None, **kwargs):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(instance=self.growlog, **self.get_form_kwargs())

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['growlog'] = self.growlog
        return context

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=pk)
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            return HttpResponse(status=403)

        return render(request, self.template_name, context=self.get_context_data())

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=pk)
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            return HttpResponse(status=403)

        form = self.form_class(request.POST, instance=self.growlog)

        if form.is_valid():
            form.save(commit=True)

        return render(request, self.success_template_name, context=self.get_context_data())


class HxGrowlogActiveInfoView(LoginRequiredMixin, BaseView):
    template_name = GROW_TEMPLATES['grow/growlog/hx-active_info']

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = dict(kwargs)

        page = kwargs.get('active_growlogs_page', 1)
        if 'active_growlogs_page' in self.request.GET:
            try:
                page = int(self.request.GET['active_growlogs_page'])
            except ValueError:
                pass
        paginate = GROW_USER_SETTINGS['paginate']
        if 'active_growlogs_paginate' in self.request.GET:
            try:
                paginate = int(self.request.GET['active_growlogs_paginate'])
            except ValueError:
                pass

        active_growlogs = self.request.user.growlogs.filter(
            finished_at__isnull=True
        ).order_by('-started_at')

        n_active_growlogs = active_growlogs.count()

        if not n_active_growlogs:
            active_growlogs_n_pages = 1
        else:
            active_growlogs_n_pages = (n_active_growlogs - 1) // paginate + 1

        if page < 1:
            page = 1
        elif page > active_growlogs_n_pages:
            page = active_growlogs_n_pages

        context['active_growlogs_paginate'] = paginate
        context['active_growlogs_current_page'] = page
        context['active_growlogs_n_pages'] = active_growlogs_n_pages
        context['n_active_growlogs'] = n_active_growlogs
        context['active_growlogs'] = active_growlogs[(page - 1) * paginate: page * paginate]

        return context

    def get(self, request: HttpRequest, **kwargs) -> HttpResponse:
        return render(request, self.template_name, context=self.get_context_data())


class HxGrowlogFinishedInfoView(BaseView):
    template_name = GROW_TEMPLATES['grow/growlog/hx-finished_info']

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = dict(kwargs)

        page = kwargs.get('finished_growlogs_page', 1)
        if 'finished_growlogs_page' in self.request.GET:
            try:
                page = int(self.request.GET['finished_growlogs_page'])
            except ValueError:
                pass
        paginate = GROW_USER_SETTINGS['paginate']
        if 'finished_growlogs_paginate' in self.request.GET:
            try:
                paginate = int(self.request.GET['finished_growlogs_paginate'])
            except ValueError:
                pass

        finished_growlogs = self.request.user.growlogs.filter(
            finished_at__isnull=False
        ).order_by('title')

        n_finished_growlogs = finished_growlogs.count()

        if not n_finished_growlogs:
            finished_growlogs_n_pages = 1
        else:
            finished_growlogs_n_pages = (n_finished_growlogs - 1) // paginate + 1

        if page < 1:
            page = 1
        elif page > finished_growlogs_n_pages:
            page = finished_growlogs_n_pages

        context['finished_growlogs_paginate'] = paginate
        context['finished_growlogs_current_page'] = page
        context['finished_growlogs_n_pages'] = finished_growlogs_n_pages
        context['n_finished_growlogs'] = n_finished_growlogs
        context['finished_growlogs'] = finished_growlogs[(page - 1) * paginate: page * paginate]

        return context

    def get(self, request: HttpRequest, **kwargs) -> HttpResponse:
        return render(request, self.template_name, context=self.get_context_data())


class GrowlogEntryCreateView(LoginRequiredMixin, FormView):
    template_name = GROW_TEMPLATES['grow/growlog/entry_create']
    form_class = GrowlogForm

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['growlog'] = self.growlog
        return context

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name, context=self.get_context_data())