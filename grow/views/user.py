from django.http import HttpRequest, HttpResponse
# from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _
from ..settings import GROW_TEMPLATES, GROW_USER_SETTINGS
from ..growapi.models import Growlog
from ._base import BaseView

from .strain import (   # noqa: F401
    # HxStrainAddToStock2View,
    HxStrainRemoveFromStockView,
)

from .seeds_in_stock import (  # noqa: F401
    HxSeedsInStockDialogView,
    HxSeedsInStockInfoView,
)

from ..paginator import QuerySetPaginator


class UserInfoView(HxSeedsInStockInfoView, BaseView):
    template_name = GROW_TEMPLATES['grow/user/info']
    seeds_in_stock_template_name = GROW_TEMPLATES['grow/seeds_in_stock/hx/info']
    active_growlogs_template_name = GROW_TEMPLATES['grow/growlog/hx/active_info']
    finished_growlogs_template_name = GROW_TEMPLATES['grow/growlog/hx/finished_info']

    def get_context_data(self, **kwargs):

        settings = GROW_USER_SETTINGS(self.request)
        paginate = settings.paginate

        n_growlogs = Growlog.objects.filter(grower=self.request.user).count()
        active_growlogs_page = self.request.GET.get(
            'active_growlogs_page',
            self.request.GET.get(
                'agl_page',
                self.request.GET.get('agl_p', 1),
            )
        )
        active_growlogs_paginate_by = self.request.GET.get(
            'active_growlogs_paginate_by',
            self.request.GET.get(
                'agl_paginate_by',
                self.request.GET.get(
                    'agl_pgn',
                    self.request.GET.get(
                        'paginate_by',
                        self.request.GET.get('pgn', paginate)
                    )
                )
            )
        )
        active_growlogs = Growlog.objects.filter(
            grower=self.request.user,
            finished_at__isnull=True).order_by('-started_at')
        active_growlogs_paginator = QuerySetPaginator(
            active_growlogs,
            url_path='grow:hx-growlog-active-info',
            paginate_by=active_growlogs_paginate_by,
            page=active_growlogs_page
        )

        finished_growlogs = Growlog.objects.filter(
            grower=self.request.user,
            finished_at__isnull=False).order_by('name')

        finished_growlogs_page = self.request.GET.get(
            'finished_growlogs_page',
            self.request.GET.get(
                'fgl_page',
                self.request.GET.get('fgl_p', 1),
            )
        )
        n_active_growlogs = active_growlogs.count()

        finished_growlogs_paginate_by = self.request.GET.get(
            'finished_growlogs_paginate_by',
            self.request.GET.get(
                'fgl_paginate_by',
                self.request.GET.get(
                    'fgl_pgn',
                    self.request.GET.get(
                        'paginate_by',
                        self.request.GET.get('pgn', paginate)
                    )
                )
            )
        )

        finished_growlogs_paginator = QuerySetPaginator(
            finished_growlogs,
            url_path='grow:hx-growlog-finished-info',
            paginate_by=finished_growlogs_paginate_by,
            page=finished_growlogs_page
        )
        n_finished_growlogs = finished_growlogs.count()

        ret = HxSeedsInStockInfoView.get_context_data(self,
                                                      seeds_in_stock_render_text=True,
                                                      seeds_in_stock_render_user_text=False,
                                                      seeds_in_stock_render_table=True,
                                                      **kwargs)
        ret.update({
            'seeds_in_stock_template': self.seeds_in_stock_template_name,
            'seeds_in_stock_user': self.request.user,
            'n_growlogs': n_growlogs,
            'active_growlogs_paginator': active_growlogs_paginator,
            'finished_growlogs_paginator': finished_growlogs_paginator,
            'n_active_growlogs': n_active_growlogs,
            'n_finished_growlogs': n_finished_growlogs,
            'active_growlogs': active_growlogs,
            'active_growlogs_template': self.active_growlogs_template_name,
            'active_growlogs_paginate': paginate,
            'finished_growlogs': finished_growlogs,
            'finished_growlogs_template': self.finished_growlogs_template_name,
            'finished_growlogs_paginate': paginate,
        })
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
