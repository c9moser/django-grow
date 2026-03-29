from typing import Any
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, FormView
from django.db.models import Count

# from grow.growapi import settings

from grow.forms.growlog import (
    GrowlogAddStrainForm,
    GrowlogDeleteForm,
    GrowlogEntryForm,
    GrowlogEntryImageUpdateForm,
    GrowlogForm,
    GrowlogDescriptionForm,
    GrowlogNotesForm,
    GrowlogQuantityForm,
    GrowlogSeedsFromStockForm,
    GrowlogStrainDeleteForm,
    GrowlogEntryImageForm,
)

# from grow.growapi.models.strain import Strain
from ..growapi.models import (
    Growlog,
    GrowlogEntry,
    GrowlogEntryImage,
    GrowlogStrain,
    Breeder,
)
# from django.urls import reverse

from ..settings import GROW_TEMPLATES, GROW_USER_SETTINGS

from ._base import BaseView
from ..growapi.permission import (
    growlog_user_is_allowed_to_view,
    growlog_user_is_allowed_to_edit,
)

from ..paginator import QuerySetPaginator


class GrowlogDetailView(BaseView):
    template_name = GROW_TEMPLATES['grow/growlog/detail']
    strains_template_name = GROW_TEMPLATES['grow/growlog/growlog/hx/strains']
    entries_template_name = GROW_TEMPLATES['grow/growlog/growlog/hx/entries']

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        growlog = get_object_or_404(Growlog, pk=pk)

        if not growlog_user_is_allowed_to_view(request.user, growlog):
            raise PermissionDenied(_("You do not have permission to view this growlog."))

        growlog_strains = GrowlogStrain.objects.filter(growlog=growlog).order_by(
            'strain__name', 'strain__breeder__name')
        if (growlog_user_is_allowed_to_edit(request.user, growlog) and not growlog.is_finished):
            entries = growlog.entries.all().order_by('-timestamp')
        else:
            entries = growlog.entries.filter().order_by('timestamp')

        entries_paginator = QuerySetPaginator(
            entries,
            paginate_by=5,
            page=request.GET.get('entries_page', 1)
        )

        context = {
            'growlog': growlog,
            'growlog_strains': growlog_strains,
            'growlog_entries': entries,
            'can_edit': growlog_user_is_allowed_to_edit(request.user, growlog),
            'strains_template': self.strains_template_name,
            'entries_template': self.entries_template_name,
            'notes_template': GROW_TEMPLATES['grow/growlog/growlog/hx/notes'],
            'description_template': GROW_TEMPLATES['grow/growlog/growlog/hx/description'],
            'entries_paginator': entries_paginator,
        }
        return render(request, self.template_name, context)


class MyGrowlogsView(LoginRequiredMixin, BaseView):
    template_name = GROW_TEMPLATES['grow/growlog/my_growlogs']

    def get(self, request: HttpRequest) -> HttpResponse:
        active_growlogs = Growlog.objects.filter(
            grower=request.user,
            finished_at__isnull=True
        ).order_by('-started_at')

        finished_growlogs = Growlog.objects.filter(
            grower=request.user,
            finished_at__isnull=False
        ).order_by('name')

        context = {
            'active_growlogs': active_growlogs,
            'finished_growlogs': finished_growlogs,
            'strains_grown': GrowlogStrain.objects.filter(
                growlog__grower=request.user
            ).order_by(
                'strain__name',
                'strain__breeder__name',
                'growlog__name',
            )
        }
        return render(request, self.template_name, context)


class HxGrowlogEntriesView(BaseView):
    template_name = GROW_TEMPLATES['grow/growlog/growlog/hx/entries']

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        entries = self.growlog.entries.filter().order_by('timestamp')
        can_edit = False
        if growlog_user_is_allowed_to_edit(self.request.user, self.growlog):
            can_edit = True
            if not self.growlog.is_finished:
                entries = self.growlog.entries.all().order_by('-timestamp')

        entries_page = int(self.request.GET.get(
            'entries_page',
            self.request.GET.get(
                'page',
                self.request.GET.get('p', 1)
            )
        ))
        entries_paginate_by = int(self.request.GET.get(
            'entries_paginate_by',
            self.request.GET.get(
                'paginate_by',
                self.request.GET.get('pgn', 5)
            )
        ))
        entries_paginator = QuerySetPaginator(
            entries,
            paginate_by=entries_paginate_by,
            page=entries_page
        )

        context = {
            'growlog': self.growlog,
            'entries_paginator': entries_paginator,
            'can_edit': can_edit,
        }
        context.update(kwargs)
        return context

    def get(self, request: HttpRequest, growlog_pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=growlog_pk)
        if not growlog_user_is_allowed_to_view(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to view this growlog."))

        return render(request, self.template_name, self.get_context_data())


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

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.instance = self.get_object()
        if not growlog_user_is_allowed_to_edit(request.user, self.instance):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))
        return super().dispatch(request, *args, **kwargs)


class GrowlogSetGerminatingAtView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=pk)
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))
        if (
            not self.growlog.germinating_at
            and not self.growlog.flowering_at
            and not self.growlog.vegetative_at
            and not self.growlog.cutted_at
            and not self.growlog.harvested_at
            and not self.growlog.finished_at
        ):
            self.growlog.germinating_at = timezone.now().date()
            self.growlog.save()
        return redirect(reverse('grow:growlog-detail', kwargs={'pk': self.growlog.pk}))


class GrowlogUnsetGerminatingAtView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=pk)
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))

        if (
            self.growlog.germinating_at
            and not self.growlog.flowering_at
            and not self.growlog.vegetative_at
            and not self.growlog.cutted_at
            and not self.growlog.harvested_at
            and not self.growlog.finished_at
        ):
            self.growlog.germinating_at = None
            self.growlog.save()
        return redirect(reverse('grow:growlog-detail', kwargs={'pk': self.growlog.pk}))


class GrowlogSetCuttedAtView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=pk)
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))
        if (
            not self.growlog.cutted_at
            and not self.growlog.harvested_at
            and not self.growlog.finished_at
            and not self.growlog.flowering_at
            and not self.growlog.vegetative_at
            and not self.growlog.germinating_at
        ):
            self.growlog.cutted_at = timezone.now().date()
            self.growlog.save()
        return redirect(reverse('grow:growlog-detail', kwargs={'pk': self.growlog.pk}))


class GrowlogUnsetCuttedAtView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=pk)
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))
        if (
            self.growlog.cutted_at
            and not self.growlog.harvested_at
            and not self.growlog.finished_at
            and not self.growlog.flowering_at
        ):
            self.growlog.cutted_at = None
            self.growlog.save()
        return redirect(reverse('grow:growlog-detail', kwargs={'pk': self.growlog.pk}))


class GrowlogSetVegetativeAtView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=pk)
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))
        if (
            not self.growlog.vegetative_at
            and not self.growlog.flowering_at
            and not self.growlog.harvested_at
            and not self.growlog.finished_at
        ):
            self.growlog.vegetative_at = timezone.now().date()
            self.growlog.save()
        return redirect(reverse('grow:growlog-detail', kwargs={'pk': self.growlog.pk}))


class GrowlogUnsetVegetativeAtView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=pk)
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))
        if (
            self.growlog.vegetative_at
            and not self.growlog.flowering_at
            and not self.growlog.harvested_at
            and not self.growlog.finished_at
        ):
            self.growlog.vegetative_at = None
            self.growlog.save()
        return redirect(reverse('grow:growlog-detail', kwargs={'pk': self.growlog.pk}))


class GrowlogSetFloweringAtView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=pk)
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))
        if (
            not self.growlog.flowering_at
            and not self.growlog.harvested_at
            and not self.growlog.finished_at
        ):
            self.growlog.flowering_at = timezone.now().date()
            self.growlog.save()
        return redirect(reverse('grow:growlog-detail', kwargs={'pk': self.growlog.pk}))


class GrowlogUnsetFloweringAtView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=pk)
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))
        if (
            self.growlog.flowering_at
            and not self.growlog.harvested_at
            and not self.growlog.finished_at
        ):
            self.growlog.flowering_at = None
            self.growlog.save()
        return redirect(reverse('grow:growlog-detail', kwargs={'pk': self.growlog.pk}))


class GrowlogSetHarvestedAtView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=pk)
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))

        if not self.growlog.harvested_at and not self.growlog.finished_at:
            self.growlog.harvested_at = timezone.now().date()
            self.growlog.save()

        return redirect(reverse('grow:growlog-detail', kwargs={'pk': self.growlog.pk}))


class GrowlogUnsetHarvestedAtView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=pk)
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))

        if self.growlog.harvested_at and not self.growlog.finished_at:
            self.growlog.harvested_at = None
            self.growlog.save()

        return redirect(reverse('grow:growlog-detail', kwargs={'pk': self.growlog.pk}))


class GrowlogSetFinishedAtView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=pk)
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))
        if not self.growlog.finished_at:
            self.growlog.finished_at = timezone.now().date()
            self.growlog.save()
        return redirect(reverse('grow:growlog-detail', kwargs={'pk': self.growlog.pk}))


class GrowlogUnsetFinishedAtView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=pk)
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))

        if self.growlog.finished_at:
            self.growlog.finished_at = None
            self.growlog.save()

        return redirect(reverse('grow:growlog-detail', kwargs={'pk': self.growlog.pk}))


class GrowlogDeleteView(LoginRequiredMixin, FormView):
    model = Growlog
    form_class = GrowlogDeleteForm
    template_name = GROW_TEMPLATES['grow/growlog/delete']

    def get_context_data(self, **kwargs):
        return super().get_context_data(growlog=self.growlog, **kwargs)

    def get_success_url(self) -> str:
        return reverse('grow:user-info')

    def form_valid(self, form):
        if form.cleaned_data['confirm']:
            self.growlog.delete()
            return redirect(self.get_success_url())
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)

    def get(self, request: HttpRequest, pk, **kwargs) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=pk)  # check if growlog exists

        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to delete this growlog."))

        return super().get(request, pk=pk, **kwargs)

    def post(self, request: HttpRequest, pk, **kwargs) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=pk)  # check if growlog exists

        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to delete this growlog."))

        form = self.form_class(request.POST)
        if form.is_valid():
            self.growlog.delete()
            return redirect(self.get_success_url())
        else:
            return super().post(request, pk=pk, **kwargs)


class HxGrowlogStrainsInfoView(BaseView):
    template_name = GROW_TEMPLATES['grow/growlog/growlog/hx/strains']

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = kwargs
        context["growlog"] = self.growlog
        context["growlog_strains"] = GrowlogStrain.objects.filter(growlog=self.growlog).order_by(
            'strain__name', 'strain__breeder__name')
        context["can_edit"] = growlog_user_is_allowed_to_edit(self.request.user, self.growlog)
        return context

    def get(self, request: HttpRequest, growlog_pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=growlog_pk)

        if not growlog_user_is_allowed_to_view(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to view this growlog."))

        return render(request, self.template_name, self.get_context_data())


class HxGrowlogAddSeedsView(LoginRequiredMixin, HxGrowlogStrainsInfoView, FormView):
    template_name = GROW_TEMPLATES['grow/growlog/growlog/hx/seeds_add']
    info_template_name = GROW_TEMPLATES['grow/growlog/growlog/hx/strains']
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
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))

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
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))

        form = GrowlogSeedsFromStockForm(request.POST, user=request.user)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class HxGrowlogAddPlantsView(LoginRequiredMixin, HxGrowlogStrainsInfoView, FormView):
    template_name = GROW_TEMPLATES['grow/growlog/growlog/hx/add_plants']
    result_template_name = GROW_TEMPLATES['grow/growlog/growlog/hx/strains']
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
            raise PermissionDenied(_("You do not have permission to edit this growlog."))

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
    template_name = GROW_TEMPLATES['grow/growlog/growlog/hx/remove_plants']
    result_template_name = GROW_TEMPLATES['grow/growlog/growlog/hx/strains']
    form_class = GrowlogQuantityForm

    def get_context_data(self, **kwargs):
        return FormView.get_context_data(
            self,
            **HxGrowlogStrainsInfoView.get_context_data(self, **kwargs)
        )

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.growlog_strain = get_object_or_404(GrowlogStrain, pk=pk)
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog_strain.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))

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
            raise PermissionDenied(_("You do not have permission to edit this growlog."))

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
    template_name = GROW_TEMPLATES['grow/growlog/growlog/hx/add_strain']
    result_template_name = GROW_TEMPLATES['grow/growlog/growlog/hx/strains']
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
            raise PermissionDenied(_("You do not have permission to edit this growlog."))

        return render(request, self.template_name, self.get_context_data(
            form=self.get_form(),
            growlog=self.growlog,
        ))

    def post(self, request: HttpRequest, growlog_pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=growlog_pk)

        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))

        form = self.form_class(request.POST)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        if form.cleaned_data['quantity'] < 0:
            form.add_error('quantity', 'Quantity cannot be negative.')
            return self.form_invalid(form)

        strain = form.cleaned_data['strain']
        self.growlog_strain = GrowlogStrain.objects.create(
            growlog=self.growlog,
            strain=strain,
            is_grown_from_seed=form.cleaned_data['is_grown_from_seed'],
            quantity=form.cleaned_data['quantity'],
        )

        return render(self.request, self.result_template_name, self.get_context_data(
            strain=strain,
            growlog=self.growlog,
            is_grown_from_seed=self.growlog_strain.is_grown_from_seed,
            quantity=self.growlog_strain.quantity,
        ))

    def form_invalid(self, form):
        return render(self.request, self.result_template_name, self.get_context_data(
            form=form,
            growlog=self.growlog,
        ))


class HxGrowlogAddStrainUpdateView(HxGrowlogAddStrainView):
    template_name = GROW_TEMPLATES['grow/growlog/growlog/hx/add_strain']

    def post(self, request: HttpRequest, growlog_pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=growlog_pk)
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))

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
            if not breeders.filter(id=breeder.id):
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
                initial['strain'] = strain.id

        initial['is_grown_from_seed'] = form.cleaned_data['is_grown_from_seed']
        initial['quantity'] = form.cleaned_data['quantity']
        result_form = self.get_form(data=initial)
        result_form.fields['strain'].queryset = strains
        result_form.fields['strain'].initial = strain.id if strain else None

        return render(request, self.template_name, self.get_context_data(
            form=result_form,
            growlog=self.growlog,
        ))


class HxGrowlogDeleteStrainView(LoginRequiredMixin, HxGrowlogStrainsInfoView, FormView):
    template_name = GROW_TEMPLATES['grow/growlog/growlog/hx/delete_strain']
    result_template_name = GROW_TEMPLATES['grow/growlog/growlog/hx/strains']

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
            raise PermissionDenied(_("You do not have permission to edit this growlog."))
        self.growlog = self.growlog_strain.growlog
        self.strain = self.growlog_strain.strain

        return render(request, self.template_name, self.get_context_data())

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.growlog_strain = get_object_or_404(GrowlogStrain, pk=pk)
        self.growlog = self.growlog_strain.growlog

        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))
        self.growlog_strain.delete()

        return render(request, self.result_template_name, self.get_context_data())


class HxGrowlogEditNotesView(LoginRequiredMixin, FormView):
    template_name = GROW_TEMPLATES['grow/growlog/growlog/hx/edit_notes']
    result_template_name = GROW_TEMPLATES['grow/growlog/growlog/hx/notes']

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
            raise PermissionDenied(_("You do not have permission to edit this growlog."))

        form = GrowlogNotesForm(request.POST, instance=self.growlog)
        if form.is_valid():
            form.save(commit=True)

        return render(request, self.result_template_name, context=self.get_context_data())


class HxGrowlogEditDescriptionView(LoginRequiredMixin, FormView):
    template_name = GROW_TEMPLATES['grow/growlog/growlog/hx/edit_description']
    result_template_name = GROW_TEMPLATES['grow/growlog/growlog/hx/description']

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
            raise PermissionDenied(_("You do not have permission to edit this growlog."))

        return render(request, self.template_name, context=self.get_context_data())

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=pk)
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))

        form = self.form_class(request.POST, instance=self.growlog)

        if form.is_valid():
            form.save(commit=True)

        return render(request, self.result_template_name, context=self.get_context_data())


class HxGrowlogActiveInfoView(LoginRequiredMixin, BaseView):
    template_name = GROW_TEMPLATES['grow/growlog/hx/active_info']

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
    template_name = GROW_TEMPLATES['grow/growlog/hx/finished_info']

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
    template_name = GROW_TEMPLATES['grow/growlog/entry/create']
    form_template_name = GROW_TEMPLATES['grow/growlog/entry/form']

    form_class = GrowlogEntryForm

    def get_form(self, form_class=None, **form_kwargs):
        if form_class is None:
            form_class = self.get_form_class()

        if 'initial' in form_kwargs:
            initial = form_kwargs['initial']
        else:
            initial = {}

        if 'data' in form_kwargs:
            data = form_kwargs['data']
        else:
            data = {}

        if self.growlog.last_location:
            initial['location'] = self.growlog.last_location.id
            data['location'] = self.growlog.last_location.id
        else:
            pass

        if 'location' in data:
            try:
                location_id = int(data['location'])
                location = self.request.user.locations.filter(id=location_id).first()
                if location:
                    initial['location'] = location.id
            except ValueError:
                pass

        form_kwargs['initial'] = initial
        form_kwargs['data'] = data

        form = form_class(**form_kwargs)
        form.fields['location'].queryset = self.request.user.locations.all().order_by('name')

        return form

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['growlog'] = self.growlog
        context['form_template'] = self.form_template_name

        context['form'].fields['location'].queryset = self.request.user.locations.all(
        ).order_by('name')

        return context

    def form_valid(self, form):
        entry = form.save(commit=False)
        entry.growlog = self.growlog
        entry.save()
        return redirect(reverse('grow:growlog-detail', kwargs={'pk': self.growlog.pk}))

    def form_invalid(self, form):
        return render(self.request, self.template_name, context=self.get_context_data(form=form))

    def get(self, request: HttpRequest, growlog_pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=growlog_pk)
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))
        return render(request, self.template_name, context=self.get_context_data())

    def post(self, request: HttpRequest, growlog_pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=growlog_pk)
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))

        form = self.form_class(request.POST)
        form.fields['location'].queryset = request.user.locations.all().order_by('name')
        form.fields['location'].initial = (
            self.growlog.last_location.id
            if self.growlog.last_location
            else None
        )

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class HxGrowlogEntryCreateView(GrowlogEntryCreateView, HxGrowlogEntriesView):
    template_name = GROW_TEMPLATES['grow/growlog/entry/hx/create']
    result_template_name = GROW_TEMPLATES['grow/growlog/growlog/hx/entries']

    def get_context_data(self, **kwargs):
        context = GrowlogEntryCreateView.get_context_data(
            self,
            **HxGrowlogEntriesView.get_context_data(self, **kwargs)
        )
        return context

    def form_valid(self, form):
        super().form_valid(form)
        return render(self.request, self.result_template_name, context=self.get_context_data())

    def form_invalid(self, form):
        return render(self.request, self.result_template_name, context=self.get_context_data())


class GrowlogEntryUpdateView(LoginRequiredMixin, FormView):
    template_name = GROW_TEMPLATES['grow/growlog/entry/update']
    form_template_name = GROW_TEMPLATES['grow/growlog/entry/form']

    form_class = GrowlogEntryForm

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['growlog'] = self.growlog
        context['form_template'] = self.form_template_name
        context['form'].fields['location'].queryset = self.request.user.locations.all(
        ).order_by('name')
        return context

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.entry = get_object_or_404(GrowlogEntry, pk=pk)
        self.growlog = self.entry.growlog

        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))

        form = self.form_class(instance=self.entry)
        return render(request, self.template_name, context=self.get_context_data(form=form))

    def form_valid(self, form):
        form.save(commit=True)
        return redirect(reverse('grow:growlog-detail', kwargs={'pk': self.growlog.pk}))

    def form_invalid(self, form):
        return super().form_invalid(form)

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.entry = get_object_or_404(GrowlogEntry, pk=pk)
        self.growlog = self.entry.growlog
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))

        form = self.form_class(request.POST, instance=self.entry)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class HxGrowlogEntryUpdateView(GrowlogEntryUpdateView, HxGrowlogEntriesView):
    template_name = GROW_TEMPLATES['grow/growlog/entry/hx/update']
    result_template_name = GROW_TEMPLATES['grow/growlog/growlog/hx/entries']

    def get_context_data(self, **kwargs):
        context = GrowlogEntryUpdateView.get_context_data(
            self,
            **HxGrowlogEntriesView.get_context_data(self, **kwargs)
        )
        return context

    def form_valid(self, form):
        super().form_valid(form)
        return render(self.request, self.result_template_name, context=self.get_context_data())

    def form_invalid(self, form):
        return render(self.request, self.result_template_name, context=self.get_context_data())


class GrowlogEntryDeleteView(LoginRequiredMixin, DeleteView):
    model = GrowlogEntry
    template_name = GROW_TEMPLATES['grow/growlog/entry/delete']
    form_class = GrowlogDeleteForm

    def get_success_url(self) -> str:
        return reverse('grow:growlog-detail', kwargs={'pk': self.growlog.pk})

    def get_context_data(self, **kwargs):
        kwargs['entry'] = self.entry
        kwargs['growlog'] = self.growlog

        return super().get_context_data(**kwargs)

    def get(self, request: HttpRequest, pk: int):
        self.entry = get_object_or_404(GrowlogEntry, pk=pk)
        self.growlog = self.entry.growlog
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))

        return super().get(request, pk=pk)

    def form_valid(self, form):
        self.entry.delete()
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        return redirect(reverse('grow:growlog-detail', kwargs={'pk': self.growlog.pk}))

    def post(self, request: HttpRequest, pk, **kwargs) -> HttpResponse:
        self.entry = get_object_or_404(GrowlogEntry, pk=pk)
        self.object = self.entry
        self.growlog = self.entry.growlog

        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))

        form = self.form_class(request.POST)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class HxGrowlogEntryDeleteView(GrowlogEntryDeleteView, HxGrowlogEntriesView):
    template_name = GROW_TEMPLATES['grow/growlog/entry/hx/delete']
    result_template_name = GROW_TEMPLATES['grow/growlog/growlog/hx/entries']

    def get_context_data(self, **kwargs):
        context = GrowlogEntryDeleteView.get_context_data(
            self,
            **HxGrowlogEntriesView.get_context_data(self, **kwargs)
        )
        return context

    def form_valid(self, form):
        GrowlogEntryDeleteView.form_valid(self, form)
        return render(self.request, self.result_template_name, context=self.get_context_data())

    def form_invalid(self, form):
        return render(self.request, self.result_template_name, context=self.get_context_data())


class GrowlogEntryUploadImageView(LoginRequiredMixin, FormView):
    template_name = GROW_TEMPLATES['grow/growlog/entry/image/upload']
    form_class = GrowlogEntryImageForm

    def get_context_data(self, **kwargs):
        kwargs.setdefault('growlog_entry', self.entry)
        kwargs.setdefault('growlog', self.growlog)

        context = FormView.get_context_data(
            self,
            **HxGrowlogEntriesView.get_context_data(self, **kwargs)
        )
        return context

    def get(self, request: HttpRequest, entry_pk: int) -> HttpResponse:
        self.entry = get_object_or_404(GrowlogEntry, pk=entry_pk)
        self.growlog = self.entry.growlog

        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))

        form = self.form_class()
        return render(request, self.template_name, context=self.get_context_data(form=form))

    def post(self, request: HttpRequest, entry_pk: int) -> HttpResponse:
        self.entry = get_object_or_404(GrowlogEntry, pk=entry_pk)
        self.growlog = self.entry.growlog

        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))

        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            image = form.save(commit=False)
            image.growlog_entry = self.entry
            image.save()
            return redirect(reverse('grow:growlog-detail', kwargs={'pk': self.growlog.pk}))
        else:
            return render(request, self.template_name, context=self.get_context_data(form=form))


class HxGrowlogEntryUploadImageView(GrowlogEntryUploadImageView,
                                    HxGrowlogEntriesView):
    template_name = GROW_TEMPLATES['grow/growlog/entry/image/hx/upload']
    result_template_name = GROW_TEMPLATES['grow/growlog/growlog/hx/entries']

    def get_context_data(self, **kwargs):
        kwargs.setdefault('growlog_entry', self.entry)
        kwargs.setdefault('growlog', self.growlog)

        context = FormView.get_context_data(
            self,
            **HxGrowlogEntriesView.get_context_data(self, **kwargs)
        )
        return context

    def get(self, request: HttpRequest, entry_pk: int) -> HttpResponse:
        self.entry = get_object_or_404(GrowlogEntry, pk=entry_pk)
        self.growlog = self.entry.growlog

        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))

        form = self.form_class()
        return render(request, self.template_name, context=self.get_context_data(form=form))

    def post(self, request: HttpRequest, entry_pk: int) -> HttpResponse:
        self.entry = get_object_or_404(GrowlogEntry, pk=entry_pk)
        self.growlog = self.entry.growlog

        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))

        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            image = form.save(commit=False)
            image.entry = self.entry
            image.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        return render(self.request, self.result_template_name, context=self.get_context_data())

    def form_invalid(self, form):
        return render(self.request, self.result_template_name, context=self.get_context_data())


class GrowlogEntryDeleteImageView(LoginRequiredMixin, DeleteView):
    model = GrowlogEntryImage
    template_name = GROW_TEMPLATES['grow/growlog/entry/image/delete']
    form_class = GrowlogDeleteForm

    def get_success_url(self) -> str:
        return reverse('grow:growlog-detail', kwargs={'pk': self.growlog.pk})

    def get_context_data(self, **kwargs):
        kwargs['image'] = self.image
        kwargs['entry'] = self.entry
        kwargs['growlog'] = self.growlog

        return super().get_context_data(**kwargs)

    def get(self, request: HttpRequest, pk: int):
        self.image = get_object_or_404(GrowlogEntryImage, pk=pk)
        self.entry = self.image.growlog_entry
        self.growlog = self.entry.growlog
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))

        return super().get(request, pk=pk)

    def form_valid(self, form):
        print("Deleting image with id", self.image.id)
        self.image.delete()
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        print("Form invalid with errors:", form.errors)
        return redirect(reverse('grow:growlog-detail', kwargs={'pk': self.growlog.pk}))

    def post(self, request: HttpRequest, pk, **kwargs) -> HttpResponse:
        self.image = get_object_or_404(GrowlogEntryImage, pk=pk)
        self.object = self.image
        self.entry = self.image.growlog_entry
        self.growlog = self.entry.growlog

        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))

        form = self.form_class(request.POST)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_object_name(self, object):
        return 'image'


class HxGrowlogEntryDeleteImageView(GrowlogEntryDeleteImageView,
                                    HxGrowlogEntriesView):
    template_name = GROW_TEMPLATES['grow/growlog/entry/image/hx/delete']
    result_template_name = GROW_TEMPLATES['grow/growlog/growlog/hx/entries']

    def get_context_data(self, **kwargs):
        context = GrowlogEntryDeleteImageView.get_context_data(
            self,
            **HxGrowlogEntriesView.get_context_data(self, **kwargs)
        )
        return context

    def form_valid(self, form):
        GrowlogEntryDeleteImageView.form_valid(self, form)
        return render(self.request, self.result_template_name, context=self.get_context_data())

    def form_invalid(self, form):
        return render(self.request, self.result_template_name, context=self.get_context_data())


class GrowlogEntryUpdateImageView(LoginRequiredMixin, FormView):
    template_name = GROW_TEMPLATES['grow/growlog/entry/image/update']
    form_class = GrowlogEntryImageUpdateForm

    def get_context_data(self, **kwargs):
        kwargs.setdefault('image', self.image)
        kwargs.setdefault('entry', self.entry)
        kwargs.setdefault('growlog', self.growlog)

        context = FormView.get_context_data(
            self,
            **HxGrowlogEntriesView.get_context_data(self, **kwargs)
        )
        return context

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.image = get_object_or_404(GrowlogEntryImage, pk=pk)
        self.entry = self.image.growlog_entry
        self.growlog = self.entry.growlog

        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))

        form = self.form_class(instance=self.image)
        return render(request, self.template_name, context=self.get_context_data(form=form))

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.image = get_object_or_404(GrowlogEntryImage, pk=pk)
        self.entry = self.image.growlog_entry
        self.growlog = self.entry.growlog

        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))

        form = self.form_class(request.POST, instance=self.image)

        if form.is_valid():
            self.image = form.save(commit=True)
            return redirect(reverse('grow:growlog-detail', kwargs={'pk': self.growlog.pk}))
        else:
            print(form.errors)
            return render(request, self.template_name, context=self.get_context_data(form=form))


class HxGrowlogEntryUpdateImageView(GrowlogEntryUpdateImageView, HxGrowlogEntriesView):
    template_name = GROW_TEMPLATES['grow/growlog/entry/image/hx/update']
    result_template_name = GROW_TEMPLATES['grow/growlog/growlog/hx/entries']

    def get_context_data(self, **kwargs):
        context = GrowlogEntryUpdateImageView.get_context_data(
            self,
            **HxGrowlogEntriesView.get_context_data(self, **kwargs)
        )
        return context

    def form_valid(self, form):
        image = form.save(commit=False)
        image.save()
        return render(self.request, self.result_template_name, context=self.get_context_data())

    def form_invalid(self, form):
        return render(self.request, self.result_template_name, context=self.get_context_data())


class MyStrainsGrownView(LoginRequiredMixin, BaseView):
    template_name = GROW_TEMPLATES['grow/growlog/strains_grown']

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        strains_grown = GrowlogStrain.objects.filter(
            growlog__grower=self.request.user,
            quantity__gt=0,
        ).order_by('strain__name', 'strain__breeder__name')

        context = dict(kwargs)
        context['strains_grown'] = strains_grown
        return context

    def get(self, request: HttpRequest, **kwargs) -> HttpResponse:
        return render(request, self.template_name, context=self.get_context_data())
