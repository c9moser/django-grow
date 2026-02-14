from django.http import HttpRequest, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from ..settings import GROW_TEMPLATES
from ..growapi.models import StrainsInStock, Growlog
from ._base import BaseView

from .strain import (
    HxStrainAddToStockView,
    HxStrainRemoveFromStockView,
)


class UserInfoView(LoginRequiredMixin, BaseView):
    template_name = GROW_TEMPLATES['grow/user/info']

    def get(self, request: HttpRequest) -> HttpResponse:
        seeds_in_stock: list[StrainsInStock] = StrainsInStock.objects.filter(
            user=request.user, quantity__gt=0).order_by(
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

        n_growlogs = Growlog.objects.filter(grower=request.user).count()
        active_growlogs = Growlog.objects.filter(
            grower=request.user,
            finished_at__isnull=True).order_by('-started_at')
        n_active_growlogs = active_growlogs.count()
        finished_growlogs = Growlog.objects.filter(
            grower=request.user,
            finished_at__isnull=False).order_by('-started_at')
        n_finished_growlogs = finished_growlogs.count()

        return render(request, self.template_name, {
            'seeds_in_stock': seeds_in_stock,
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
        })


class RenderUserInfoInStockMixin:
    info_in_stock_template_name = GROW_TEMPLATES['grow/user/hx-info_seeds_in_stock']

    def render_info_in_stock(self, request: HttpRequest) -> HttpResponse:
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

        return render(request, self.info_in_stock_template_name, {
            'seeds_in_stock': seeds_in_stock,
            'n_seeds_in_stock': n_seeds_in_stock,
            'n_feminized_seeds_in_stock': n_feminized_seeds_in_stock,
            'n_regular_seeds_in_stock': n_regular_seeds_in_stock,
            'n_autoflowering_seeds_in_stock': n_autoflowering_seeds_in_stock,
            'n_photoperiod_seeds_in_stock': n_photoperiod_seeds_in_stock,
        })


class HxUserInfoAddSeedsToStockView(RenderUserInfoInStockMixin, HxStrainAddToStockView):
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


class HxUserInfoRemoveSeedsFromStockView(RenderUserInfoInStockMixin, HxStrainRemoveFromStockView):
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
