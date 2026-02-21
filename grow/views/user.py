from django.http import HttpRequest, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from ..settings import GROW_TEMPLATES, GROW_USER_SETTINGS
from ..growapi.models import StrainsInStock, Growlog
from ._base import BaseView

from .strain import (
    HxStrainAddToStockView,
    HxStrainRemoveFromStockView,
    HxSeedsInStockInfoView,
)


class UserInfoView(LoginRequiredMixin, BaseView):
    template_name = GROW_TEMPLATES['grow/user/info']
    seeds_in_stock_template_name = GROW_TEMPLATES['grow/strain/hx-seeds_in_stock_info']

    def get_context_data(self, **kwargs):
        user_settings = GROW_USER_SETTINGS(self.request)
        seeds_in_stock: list[StrainsInStock] = StrainsInStock.objects.filter(
            user=self.request.user, quantity__gt=0).order_by(
            'strain__name', 'strain__breeder__name')
        n_seeds_in_stock = 0
        n_feminized_seeds_in_stock = 0
        n_regular_seeds_in_stock = 0
        n_autoflowering_seeds_in_stock = 0
        n_photoperiod_seeds_in_stock = 0

        for seeds in seeds_in_stock:
            n_seeds_in_stock += seeds.quantity
            if seeds.is_feminized:
                n_feminized_seeds_in_stock += seeds.quantity
            elif seeds.is_regular:
                n_regular_seeds_in_stock += seeds.quantity
            if seeds.strain.is_automatic:
                n_autoflowering_seeds_in_stock += seeds.quantity
            else:
                n_photoperiod_seeds_in_stock += seeds.quantity

        paginate = user_settings.paginate
        paginate = 10
        n = seeds_in_stock.count()
        if n == 0:
            seeds_in_stock_n_pages = 1
        else:
            seeds_in_stock_n_pages = (n - 1) // paginate + 1

        seeds_in_stock_current_page = 1
        if 'sispage' in self.request.GET:
            try:
                seeds_in_stock_current_page = int(self.request.GET['sispage'])
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
        n_active_growlogs = active_growlogs.count()
        finished_growlogs = Growlog.objects.filter(
            grower=self.request.user,
            finished_at__isnull=False).order_by('-started_at')
        n_finished_growlogs = finished_growlogs.count()

        ret = {
            'seeds_in_stock_template': self.seeds_in_stock_template_name,
            'seeds_in_stock': seeds_in_stock[
                (seeds_in_stock_current_page - 1) * paginate:
                    (seeds_in_stock_current_page * paginate)],
            'seeds_in_stock_render_text': True,
            'seeds_in_stock_render_user_text': False,
            'seeds_in_stock_render_table': True,
            'seeds_in_stock_current_page': seeds_in_stock_current_page,
            'seeds_in_stock_n_pages': seeds_in_stock_n_pages,
            'seeds_in_stock_paginate': paginate,
            'n_seeds_in_stock': n_seeds_in_stock,
            'n_feminized_seeds_in_stock': n_feminized_seeds_in_stock,
            'n_regular_seeds_in_stock': n_regular_seeds_in_stock,
            'n_autoflowering_seeds_in_stock': n_autoflowering_seeds_in_stock,
            'n_photoperiod_seeds_in_stock': n_photoperiod_seeds_in_stock,
            'n_growlogs': n_growlogs,
            'n_active_growlogs': n_active_growlogs,
            'n_finished_growlogs': n_finished_growlogs,
            'active_growlogs': active_growlogs,
            'finished_growlogs': finished_growlogs,
        }
        ret.update(kwargs)
        return ret

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name, self.get_context_data())


class HxUserSeedsInStockView(HxSeedsInStockInfoView):
    render_text = True
    render_user_text = False
    render_table = True


class HxUserInfoAddSeedsToStockView(HxStrainAddToStockView):
    parent_template = GROW_TEMPLATES['grow/strain/hx-add_to_stock']
    template_name = GROW_TEMPLATES['grow/user/hx-add_seeds_to_stock']

    def get_context_data(self, **kwargs):
        context = super(HxUserInfoAddSeedsToStockView, self).get_context_data(**kwargs)
        context['parent_template'] = self.parent_template
        return context

    def form_valid(self, form):
        super().form_valid(form)
        return self.render_info_in_stock(self.request)

    def form_invalid(self, form):
        super().form_invalid(form)
        return self.render_info_in_stock(self.request)


class HxUserInfoRemoveSeedsFromStockView(HxStrainRemoveFromStockView):
    parent_template = GROW_TEMPLATES['grow/strain/hx-remove_from_stock']
    template_name = GROW_TEMPLATES['grow/user/hx-remove_seeds_from_stock']

    def get_context_data(self, **kwargs):
        context = super(HxUserInfoRemoveSeedsFromStockView, self).get_context_data(**kwargs)
        context['parent_template'] = self.parent_template
        return context

    def form_valid(self, form):
        super().form_valid(form)
        return self.render_info_in_stock(self.request)

    def form_invalid(self, form):
        super().form_invalid(form)
        return self.render_info_in_stock(self.request)
