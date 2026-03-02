from typing import Any
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from django.http import HttpRequest, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView
from grow.forms.growlog import GrowlogForm, GrowlogStrainFormSet  # noqa: F401
# from django.urls import reverse

from ..settings import GROW_TEMPLATES, GROW_USER_SETTINGS
from ..growapi.models import Growlog, GrowlogEntry, GrowlogStrain
from ._base import BaseView


class GrowlogDetailView(BaseView):
    template_name = GROW_TEMPLATES['grow/growlog/detail']

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        growlog = get_object_or_404(Growlog, pk=pk)
        growlog_strains = GrowlogStrain.objects.filter(growlog=growlog).order_by(
            'strain__name', 'strain__breeder__name')
        entries = GrowlogEntry.objects.filter(growlog=growlog).order_by('-timestamp')
        context = {
            'growlog': growlog,
            'growlog_strains': growlog_strains,
            'entries': entries,
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
        context['strains'] = GrowlogStrainFormSet(queryset=GrowlogStrain.objects.none())
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
        context['strains'] = GrowlogStrainFormSet(instance=self.object)
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
