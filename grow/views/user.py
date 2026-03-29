from django.http import HttpRequest, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from ..settings import GROW_TEMPLATES, GROW_USER_SETTINGS
from ..growapi.models import StrainsInStock, Growlog
from ._base import BaseView

from .strain import (   # noqa: F401
    HxSeedsInStockDialogView,
    HxStrainAddToStock2View,
    HxStrainRemoveFromStockView,
    HxSeedsInStockInfoView,
)

from ..paginator import QuerySetPaginator


class UserInfoView(LoginRequiredMixin, BaseView):
    template_name = GROW_TEMPLATES['grow/user/info']
    seeds_in_stock_template_name = GROW_TEMPLATES['grow/seeds_in_stock/hx/info']
    active_growlogs_template_name = GROW_TEMPLATES['grow/growlog/hx/active_info']
    finished_growlogs_template_name = GROW_TEMPLATES['grow/growlog/hx/finished_info']

    def get_context_data(self, **kwargs):
        user_settings = GROW_USER_SETTINGS(self.request)
        seeds_in_stock = StrainsInStock.objects.filter(
            user=self.request.user, quantity__gt=0).order_by(
            'strain__name', 'strain__breeder__name')
        n_seeds_in_stock = seeds_in_stock.count()
        n_feminized_seeds_in_stock = seeds_in_stock.filter(is_feminized=True).count()
        n_regular_seeds_in_stock = seeds_in_stock.filter(is_regular=True).count()
        n_autoflowering_seeds_in_stock = seeds_in_stock.filter(strain__is_automatic=True).count()
        n_photoperiod_seeds_in_stock = seeds_in_stock.filter(strain__is_automatic=False).count()

        seeds_in_stock_paginator = QuerySetPaginator(
            seeds_in_stock,
            user_settings.paginate,
            self.request.GET.get('sis_page', 1)
        )

        paginate = user_settings.paginate
        paginate = 10
        n = seeds_in_stock.count()
        if n == 0:
            seeds_in_stock_n_pages = 1
        else:
            seeds_in_stock_n_pages = (n - 1) // paginate + 1

        seeds_in_stock_current_page = 1
        if 'seeds_in_stock_page' in self.request.GET:
            try:
                seeds_in_stock_current_page = int(self.request.GET['seeds_in_stock_page'])
            except ValueError:
                pass
        if seeds_in_stock_current_page < 1:
            seeds_in_stock_current_page = 1
        elif seeds_in_stock_current_page > seeds_in_stock_n_pages:
            seeds_in_stock_current_page = seeds_in_stock_n_pages

        n_growlogs = Growlog.objects.filter(grower=self.request.user).count()
        active_growlogs = Growlog.objects.filter(
            grower=self.request.user,
            finished_at__isnull=True).order_by('-started_at')
        active_growlogs_n_pages = (active_growlogs.count() - 1) // paginate + 1
        active_growlogs_current_page = 1
        if 'active_growlogs_page' in self.request.GET:
            try:
                active_growlogs_current_page = int(self.request.GET['active_growlogs_page'])
            except ValueError:
                pass
        if active_growlogs_current_page < 1:
            active_growlogs_current_page = 1
        elif active_growlogs_current_page > active_growlogs_n_pages:
            active_growlogs_current_page = active_growlogs_n_pages
        n_active_growlogs = active_growlogs.count()
        finished_growlogs = Growlog.objects.filter(
            grower=self.request.user,
            finished_at__isnull=False).order_by('-started_at')
        n_finished_growlogs = finished_growlogs.count()
        finished_growlogs_n_pages = (n_finished_growlogs - 1) // paginate + 1
        finished_growlogs_current_page = 1
        if 'finished_growlogs_page' in self.request.GET:
            try:
                finished_growlogs_current_page = int(self.request.GET['finished_growlogs_page'])
            except ValueError:
                pass
        if finished_growlogs_current_page < 1:
            finished_growlogs_current_page = 1
        elif finished_growlogs_current_page > finished_growlogs_n_pages:
            finished_growlogs_current_page = finished_growlogs_n_pages

        ret = {
            'seeds_in_stock_template': self.seeds_in_stock_template_name,
            'seeds_in_stock': seeds_in_stock,
            'seeds_in_stock_paginator': seeds_in_stock_paginator,
            'seeds_in_stock_render_text': True,
            'seeds_in_stock_render_user_text': False,
            'seeds_in_stock_render_table': True,
            'seeds_in_stock_current_page': seeds_in_stock_current_page,
            'seeds_in_stock_n_pages': seeds_in_stock_n_pages,
            'seeds_in_stock_paginate': paginate,
            'seeds_in_stock_user': self.request.user,
            'n_seeds_in_stock': n_seeds_in_stock,
            'n_feminized_seeds_in_stock': n_feminized_seeds_in_stock,
            'n_regular_seeds_in_stock': n_regular_seeds_in_stock,
            'n_autoflowering_seeds_in_stock': n_autoflowering_seeds_in_stock,
            'n_photoperiod_seeds_in_stock': n_photoperiod_seeds_in_stock,
            'n_growlogs': n_growlogs,
            'n_active_growlogs': n_active_growlogs,
            'n_finished_growlogs': n_finished_growlogs,
            'active_growlogs': active_growlogs,
            'active_growlogs_template': self.active_growlogs_template_name,
            'active_growlogs_n_pages': active_growlogs_n_pages,
            'active_growlogs_current_page': active_growlogs_current_page,
            'active_growlogs_paginate': paginate,
            'finished_growlogs': finished_growlogs,
            'finished_growlogs_template': self.finished_growlogs_template_name,
            'finished_growlogs_n_pages': finished_growlogs_n_pages,
            'finished_growlogs_current_page': finished_growlogs_current_page,
            'finished_growlogs_paginate': paginate,
        }
        ret.update(kwargs)
        return ret

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name, self.get_context_data())


class HxUserSeedsInStockView(HxSeedsInStockInfoView):
    render_text = True
    render_user_text = False
    render_table = True


class HxUserInfoAddSeedsToStockView(HxSeedsInStockDialogView, HxUserSeedsInStockView):
    parent_template = GROW_TEMPLATES['grow/seeds_in_stock/hx/add']
    template_name = GROW_TEMPLATES['grow/user/hx-add_seeds_to_stock']
    info_template_name = GROW_TEMPLATES['grow/seeds_in_stock/hx/info']

    def get_context_data(self, **kwargs):
        context = HxSeedsInStockDialogView.get_context_data(
            self,
            **HxUserInfoAddSeedsToStockView.get_context_data(self, **kwargs))

        context['parent_template'] = self.parent_template

        if 'form' in kwargs:
            context['form'] = kwargs['form']

        return context

    def form_valid(self, form):
        super().form_valid(form)
        return render(self, self.request, self.info_template_name, **self.get_context_data())

    def form_invalid(self, form):
        super().form_invalid(form)
        return render(self, self.request, self.info_template_name, **self.get_context_data())

    def get(self, request: HttpRequest, strain) -> HttpResponse:
        return render(request, self.template_name, self.get_context_data())


class HxUserInfoRemoveSeedsFromStockView(HxStrainRemoveFromStockView, HxUserSeedsInStockView):
    parent_template = GROW_TEMPLATES['grow/strain/strain/remove_from_stock']
    template_name = GROW_TEMPLATES['grow/user/hx-remove_seeds_from_stock']
    info_template_name = GROW_TEMPLATES['grow/seeds_in_stock/hx/info']

    def get_context_data(self, **kwargs):
        context = HxStrainRemoveFromStockView.get_context_data(
            self,
            **HxUserSeedsInStockView.get_context_data(self, **kwargs)
        )
        context['parent_template'] = self.parent_template
        if 'form' not in context:
            context['form'] = kwargs.get('form', self.form_class())

        return context

    def form_valid(self, form):
        super().form_valid(form)
        return render(self.request, self.info_template_name, self.get_context_data())

    def form_invalid(self, form):
        super().form_invalid(form)
        return render(self.request, self.info_template_name, self.get_context_data())
