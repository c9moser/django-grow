from grow.growapi.models import StrainsInStock
from django.db.models import Sum, Count, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from grow.paginator import QuerySetPaginator
from grow.views._base import BaseView
from grow.views.strain import HxStrainAddToStock2View, StrainAddToStock2View, StrainAddToStock2Form
from grow import settings
import logging


class SeedsInStockInfoPaginator(QuerySetPaginator):
    urlvars = {'page': 'sis_p', 'paginate_by': 'sis_pgn'}


class HxSeedsInStockInfoView(LoginRequiredMixin, BaseView):
    template_name = settings.GROW_TEMPLATES['grow/seeds_in_stock/hx/info']
    logger = logging.getLogger(f"{__name__}.HxSeedsInStockInfoView")
    update_page_url = True

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
            self.logger.error(f"Error parsing page number: {ex}")
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

        context = kwargs
        context.setdefault('update_page_url', self.update_page_url)
        context.setdefault('n_strains_in_stock', seeds_in_stock.count())
        context.setdefault('n_seeds_in_stock', n_seeds_in_stock)
        context.setdefault('n_feminized_seeds_in_stock', n_feminized_seeds_in_stock)
        context.setdefault('n_regular_seeds_in_stock', n_regular_seeds_in_stock)
        context.setdefault('n_autoflowering_seeds_in_stock', n_autoflowering_seeds_in_stock)
        context.setdefault('n_photoperiod_seeds_in_stock', n_photoperiod_seeds_in_stock)
        context.setdefault('seeds_in_stock_render_table', render_table)
        context.setdefault('seeds_in_stock_render_text', render_text)
        context.setdefault('seeds_in_stock_render_user_text', render_user_text)
        context.update({
            'seeds_in_stock_paginator': paginator,
            'seeds_in_stock_scroll_to_card': True,
            'seeds_in_stock_user': kwargs.get('seeds_in_stock_user', self.request.user),
            'seeds_in_stock_sort': sort,
            'seeds_in_stock_ordering': ordering,
            'seeds_in_stock_update_page_url': True,
        })

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
