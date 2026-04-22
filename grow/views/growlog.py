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
    GrowlogPermissionUpdateForm,
    GrowlogEntriesViewForm,
)

# from grow.growapi.models.strain import Strain
from ..growapi.models import (
    Growlog,
    GrowlogEntry,
    GrowlogEntryImage,
    GrowlogStrain,
    Breeder,
    StrainsInStock,
)
# from django.urls import reverse

from ..settings import GROW_TEMPLATES, GROW_USER_SETTINGS


from ._base import BaseView
from ..growapi.permission import (
    growlog_user_is_allowed_to_view,
    growlog_user_is_allowed_to_edit,
)

from ..paginator import QuerySetPaginator
import logging

logger = logging.getLogger(__name__)


class HxGrowlogEntriesView(BaseView):
    template_name = GROW_TEMPLATES['grow/growlog/growlog/hx/entries']
    update_page_url = True
    hx_target = '#growlog-entries'
    filter = 'all'
    urlvars = {
        'growlog_entries_page': 'gle_pg',
        'growlog_entries_filter': 'gle_filter',
        'growlog_entries_paginate_by': 'gle_pgn',
        'growlog_entries_ordering': 'gle_ord',
    }

    def get_context_data(self, **kwargs) -> dict[str, Any]:

        can_edit = False

        user_settings = GROW_USER_SETTINGS(self.request)

        default_ordering = 'asc'
        if growlog_user_is_allowed_to_edit(self.request.user, self.growlog):
            can_edit = True
            if not self.growlog.is_finished:
                default_ordering = 'desc'
        try:
            entries_page = int(self.request.GET.get(
                'entries_page',
                self.request.GET.get(
                    'gle_page',
                    self.request.GET.get(
                        'gle_pg',
                        self.request.GET.get(
                            'gle_p',
                            self.request.GET.get(
                                'page',
                                self.request.GET.get('p', 1)
                            )
                        )
                    )
                )
            ))
        except ValueError:
            entries_page = 1

        try:
            entries_paginate_by = int(self.request.GET.get(
                'entries_paginate_by',
                self.request.GET.get(
                    'gle_paginate_by',
                    self.request.GET.get(
                        'gle_pgn',
                        self.request.GET.get(
                            'paginate_by',
                            self.request.GET.get(
                                'pgn',
                                (
                                    user_settings.growlog_paginate
                                    if user_settings else 10
                                )
                            )
                        )
                    )
                )
            ))
        except ValueError:
            entries_paginate_by = user_settings.growlog_paginate if user_settings else 10

        if hasattr(self, 'growlog_entries_ordering'):
            entries_ordering = self.growlog_entries_ordering
        else:
            entries_ordering = self.request.GET.get(
                'growlog_entries_ordering',
                self.request.GET.get(
                    'gle_ordering',
                    self.request.GET.get(
                        'gle_ord',
                        self.request.GET.get(
                            'ordering',
                            self.request.GET.get(
                                'ord', default_ordering))
                    )
                )
            )

        if hasattr(self, 'growlog_entries_filter'):
            filter = self.growlog_entries_filter
        else:
            filter = self.request.GET.get(
                'growlog_entries_filter',
                self.request.GET.get(
                    'gle_filter',
                    self.request.GET.get(
                        'gle_flt',
                        self.request.GET.get(
                            'filter',
                            self.request.GET.get('f', self.filter)
                        )
                    )
                )
            )
        gle_filters = [
            ('all', _('All')),
        ]
        has_unknonwn_filter = False
        unknown_end_date = (
            self.growlog.germinating_at
            or self.growlog.cutted_at
            or self.growlog.vegetative_at
            or self.growlog.flowering_at
            or self.growlog.harvested_at
            or self.growlog.finished_at
        )  # noqa: E501
        if self.growlog.entries.filter(timestamp__date__lt=unknown_end_date).exists():
            has_unknonwn_filter = True
            gle_filters.append(('unknown', _('Unknown')))
        if self.growlog.germinating_at:
            gle_filters.append(('germinating', _('Germinating')))
        if self.growlog.cutted_at:
            gle_filters.append(('rooting', _('Rooting')))
        if self.growlog.vegetative_at:
            gle_filters.append(('vegetative', _('Vegetative')))
        if self.growlog.flowering_at:
            gle_filters.append(('flowering', _('Flowering')))
        if self.growlog.harvested_at:
            gle_filters.append(('harvested', _('Harvested')))
        if self.growlog.finished_at:
            gle_filters.append(('finished', _('Finished')))

        if filter in ['all', 'a', '']:
            filter = 'all'
            entries = self.growlog.entries.all()
        elif filter in ['germinating', 'g', 'germ'] and self.growlog.germinating_at:
            filter = 'germinating'
            end_date = (
                self.growlog.vegetative_at
                or self.growlog.flowering_at
                or self.growlog.cutted_at
                or self.growlog.harvested_at
                or self.growlog.finished_at
                or timezone.now().date()
            )
            entries = self.growlog.entries.filter(timestamp__date__gte=self.growlog.germinating_at,
                                                  timestamp__date__lte=end_date)
        elif filter in ['rooting', 'r', 'root'] and self.growlog.cutted_at:
            filter = 'rooting'
            end_date = (
                self.growlog.vegetative_at
                or self.growlog.flowering_at
                or self.growlog.harvested_at
                or self.growlog.finished_at
                or timezone.now().date()
            )
            entries = self.growlog.entries.filter(timestamp__date__gte=self.growlog.cutted_at,
                                                  timestamp__date__lte=end_date)
        elif filter in ['vegetative', 'v', 'veg'] and self.growlog.vegetative_at:
            filter = 'vegetative'
            end_date = (
                self.growlog.flowering_at
                or self.growlog.harvested_at
                or self.growlog.finished_at
                or timezone.now().date()
            )
            entries = self.growlog.entries.filter(timestamp__date__gte=self.growlog.vegetative_at,
                                                  timestamp__date__lte=end_date)
        elif filter in ['flowering', 'f', 'flow'] and self.growlog.flowering_at:
            filter = 'flowering'
            end_date = (
                self.growlog.harvested_at
                or self.growlog.finished_at
                or timezone.now().date()
            )
            entries = self.growlog.entries.filter(timestamp__date__gte=self.growlog.flowering_at,
                                                  timestamp__date__lte=end_date)
        elif filter in ['harvested', 'h', 'harv'] and self.growlog.harvested_at:
            filter = 'harvested'
            end_date = self.growlog.finished_at or timezone.now().date()
            entries = self.growlog.entries.filter(timestamp__date__gte=self.growlog.harvested_at,
                                                  timestamp__date__lte=end_date)
        elif filter in ['finished', 'fin', 'fi'] and self.growlog.finished_at:
            filter = 'finished'
            entries = self.growlog.entries.filter(timestamp__date__gte=self.growlog.finished_at)
        elif filter in ['unknown', 'u', 'unk'] and has_unknonwn_filter:
            filter = 'unknown'
            entries = self.growlog.entries.filter(timestamp__date__lt=end_date)
        else:
            logger.warning(f"Invalid filter parameter for growlog entries: {filter}. Defaulting to all.")  # noqa: E501
            filter = 'all'
            entries = self.growlog.entries.all()

        if entries_ordering in ['asc', 'ascending', 'a', '1', 'up', 'oldest']:
            entries_ordering = 'asc'
        elif entries_ordering in ['desc', 'descending', 'd', '0', 'down', 'newest']:
            entries_ordering = 'desc'
        else:
            logger.warning(f"Invalid entries ordering parameter: {entries_ordering}. Defaulting to {default_ordering}.")  # noqa: E501
            entries_ordering = default_ordering

        if entries_ordering == 'asc':
            entries = entries.order_by('timestamp')
        else:
            entries = entries.order_by('-timestamp')

        entries_paginator = QuerySetPaginator(
            entries,
            url_path='grow:hx-growlog-entries',
            url_path_kwargs={'growlog_pk': self.growlog.pk},
            url_variables={'gle_ord': entries_ordering, 'gle_filter': filter},
            paginate_by=entries_paginate_by,
            page=entries_page
        )

        entries_form = GrowlogEntriesViewForm(initial={
            'ordering': entries_ordering,
            'filter': filter
        })
        entries_form.fields['filter'].choices = gle_filters

        context = kwargs
        context['growlog'] = self.growlog
        context['growlog_entries_paginator'] = entries_paginator
        context['can_edit'] = can_edit
        context['growlog_entries_ordering'] = entries_ordering
        context['growlog_entries_filter'] = filter
        context['growlog_entries_form'] = entries_form
        context.setdefault(
            'update_page_url',
            self.update_page_url if hasattr(self, 'update_page_url') else True
        )
        context.setdefault(
            'hx_target',
            self.hx_target if hasattr(self, 'hx_target') else '#growlog-entries'
        )

        print("HxGrowlogEntriesView: page={entries_page}, paginate_by={entries_paginate_by}, total_entries={total_entries}".format(  # noqa: E501
                        entries_page=entries_page,
                        entries_paginate_by=entries_paginate_by,
                        total_entries=entries.count()
        ))
        return context

    def get(self, request: HttpRequest, growlog_pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=growlog_pk)
        if not growlog_user_is_allowed_to_view(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to view this growlog."))

        return render(request, self.template_name, self.get_context_data())

    def post(self, request: HttpRequest, growlog_pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=growlog_pk)
        if not growlog_user_is_allowed_to_view(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to view this growlog."))

        form = GrowlogEntriesViewForm(request.POST)
        if form.is_valid():
            filter = form.cleaned_data['filter']
            ordering = form.cleaned_data['ordering']
            self.growlog_entries_ordering = ordering
            self.growlog_entries_filter = filter

            return render(request, self.template_name, self.get_context_data())
        else:
            print(f"Invalid form data: {form.errors}")
            return render(request, self.template_name, self.get_context_data(), status=400)


class HxGrowlogPermissionsUpdateView(View):
    template_name = GROW_TEMPLATES['grow/growlog/growlog/hx/permission_update']
    permission_form_class = GrowlogPermissionUpdateForm

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = kwargs
        if (
            not self.request.user.is_authenticated
            or not growlog_user_is_allowed_to_edit(self.request.user, self.growlog)
        ):
            can_edit = False
        else:
            can_edit = True
        context['growlog'] = self.growlog
        context.setdefault('permission_form', self.permission_form_class(instance=self.growlog))
        context.setdefault('growlog', self.growlog)
        context.setdefault('can_edit', can_edit)

        return context

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=pk)

        return render(request, self.template_name, self.get_context_data())

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        growlog = get_object_or_404(Growlog, pk=pk)
        if (
            not request.user.is_authenticated
            or not growlog_user_is_allowed_to_edit(request.user, growlog)
        ):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))

        form = GrowlogPermissionUpdateForm(request.POST, instance=growlog)
        if form.is_valid():
            form.save()
            return render(request, self.template_name, {'form': form, 'growlog': growlog})
        else:
            return render(request, self.template_name,
                          {'permission_form': form},
                          status=400)


class GrowlogDetailView(HxGrowlogPermissionsUpdateView, HxGrowlogEntriesView):
    template_name = GROW_TEMPLATES['grow/growlog/detail']
    strains_template_name = GROW_TEMPLATES['grow/growlog/growlog/hx/strains']
    entries_template_name = GROW_TEMPLATES['grow/growlog/growlog/hx/entries']

    def get_context_data(self, **kwargs):
        context = HxGrowlogEntriesView.get_context_data(
            self,
            **HxGrowlogPermissionsUpdateView.get_context_data(self, **kwargs))

        growlog_strains = GrowlogStrain.objects.filter(growlog=self.growlog).order_by(
            'strain__name', 'strain__breeder__name')
        context['growlog_strains'] = growlog_strains

        context.update({
            'strains_template': self.strains_template_name,
            'entries_template': self.entries_template_name,
            'notes_template': GROW_TEMPLATES['grow/growlog/growlog/hx/notes'],
            'description_template': GROW_TEMPLATES['grow/growlog/growlog/hx/description'],

        })
        return context

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=pk)

        if not growlog_user_is_allowed_to_view(request.user, self.growlog):
            if request.user.is_authenticated:
                logger.warning(f"User {request.user.username} tried to access growlog {self.growlog.pk} without permission.")  # noqa: E501
                raise PermissionDenied(_("You do not have permission to view this growlog."))
            else:
                redirect_url = reverse('account_login') + f"?next={request.path}"
                return redirect(redirect_url)

        return render(request, self.template_name, self.get_context_data())


class HxMyActiveGrowlogsView(LoginRequiredMixin, View):
    template_name = GROW_TEMPLATES['grow/growlog/hx/my_active_growlogs']
    my_active_growlogs_hx_target = '#my-active-growlogs'
    logger = logging.getLogger(__name__ + ".HxMyActiveGrowlogsView")
    urlvars = {
        'my_active_growlogs_sort': 'myagl_sort',
        'my_active_growlogs_ordering': 'myagl_ord',
    }

    def get_context_data(self, **kwargs):
        my_active_growlogs = Growlog.objects.filter(
            grower=self.request.user,
            finished_at__isnull=True
        )

        sort = self.request.GET.get(
            'my_active_growlogs_sort',
            self.request.GET.get(
                'myagl_sort',
                self.request.GET.get(
                    'myagl_s',
                    self.request.GET.get(
                        'sort',
                        self.request.GET.get('s', 'started_at')
                    )
                )
            )
        )
        ordering = self.request.GET.get(
            'my_active_growlogs_ordering',
            self.request.GET.get(
                'myagl_ordering',
                self.request.GET.get(
                    'myagl_ord',
                    self.request.GET.get(
                        'myagl_o',
                        self.request.GET.get(
                            'ordering',
                            self.request.GET.get(
                                'ord',
                                self.request.GET.get('o', 'desc')
                            )
                        )
                    )
                )
            )
        )

        if ordering in ['asc', 'ascending', 'a', '1', 'up', 'oldest']:
            ordering = 'asc'
        elif ordering in ['desc', 'descending', 'd', '0', 'down', 'newest']:
            ordering = 'desc'
        else:
            self.logger.warning(f"Invalid ordering parameter for my active growlogs: {ordering}. Defaulting to asc.")  # noqa: E501
            ordering = 'asc'

        if sort == 'started_at':
            my_active_growlogs = my_active_growlogs.order_by(
                f'{"-" if ordering == "desc" else ""}started_at'
            )
        elif sort == 'name':
            my_active_growlogs = my_active_growlogs.order_by(
                f'{"-" if ordering == "desc" else ""}name'
            )
        elif sort == 'updated_at':
            my_active_growlogs = my_active_growlogs.order_by(
                f'{"-" if ordering == "desc" else ""}updated_at',
                f'{"-" if ordering == "desc" else ""}started_at'
            )
        else:
            self.logger.warning(f"Invalid sort parameter for my active growlogs: {sort}. Defaulting to started_at.")  # noqa: E501
            ordering = 'desc'
            my_active_growlogs = my_active_growlogs.order_by('-started_at')

        context = kwargs
        context['my_active_growlogs'] = my_active_growlogs
        context['my_active_growlogs_sort'] = sort
        context['my_active_growlogs_ordering'] = ordering
        context.setdefault('hx_target', self.my_active_growlogs_hx_target)

        return context

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name, self.get_context_data())


class HxMyFinishedGrowlogsView(LoginRequiredMixin, View):
    template_name = GROW_TEMPLATES['grow/growlog/hx/my_finished_growlogs']
    urlvars = {
        'my_finished_growlogs_sort': 'myfgl_sort',
        'my_finished_growlogs_ordering': 'myfgl_ord',
    }
    my_finished_growlogs_hx_target = '#my-finished-growlogs'
    udate_page_url = True

    def get_context_data(self, **kwargs):
        context = kwargs
        context.setdefault('hx_target', self.my_finished_growlogs_hx_target)
        context.setdefault('urlvars', self.urlvars)
        context.setdefault('update_page_url', self.udate_page_url)

        finished_growlogs = Growlog.objects.filter(
            grower=self.request.user,
            finished_at__isnull=False
        )

        desc_sort = ['finished_at', 'started_at', 'updated_at']

        sort = self.request.GET.get(
            'my_finished_growlogs_sort',
            self.request.GET.get(
                'myfgl_sort',
                self.request.GET.get(
                    'myfgl_s',
                    self.request.GET.get(
                        'myfgl_sort',
                        self.request.GET.get(
                            'sort',
                            self.request.GET.get(
                                's',
                                'name'
                            )
                        )
                    )
                )
            )
        )
        ordering = self.request.GET.get(
            'my_finished_growlogs_ordering',
            self.request.GET.get(
                'myfgl_ordering',
                self.request.GET.get(
                    'myfgl_ord',
                    self.request.GET.get(
                        'ordering',
                        self.request.GET.get(
                            'ord',
                            self.request.GET.get('o', 'desc' if sort in desc_sort else 'asc')
                        )
                    )
                )
            )
        )
        if sort == 'name':
            finished_growlogs = finished_growlogs.order_by(
                f'{"-" if ordering == "desc" else ""}name'
            )
        elif sort == 'started_at':
            finished_growlogs = finished_growlogs.order_by(
                f'{"-" if ordering == "desc" else ""}started_at'
            )
        elif sort == 'updated_at':
            finished_growlogs = finished_growlogs.order_by(
                f'{"-" if ordering == "desc" else ""}updated_at',
                f'{"-" if ordering == "desc" else ""}started_at'
            )
        elif sort == 'finished_at':
            finished_growlogs = finished_growlogs.order_by(
                f'{"-" if ordering == "desc" else ""}finished_at',
                f'{"-" if ordering == "desc" else ""}started_at'
            )
        else:
            self.logger.warning(f"Invalid sort parameter for my finished growlogs: {sort}. Defaulting to finished_at.")  # noqa: E501
            sort = 'finished_at'
            ordering = 'desc'
            finished_growlogs = finished_growlogs.order_by('-finished_at', '-started_at')

        if ordering in ['asc', 'ascending', 'a', '1', 'up', 'oldest']:
            ordering = 'asc'
        elif ordering in ['desc', 'descending', 'd', '0', 'down', 'newest']:
            ordering = 'desc'
        else:
            self.logger.warning(f"Invalid ordering parameter for my finished growlogs: {ordering}. Defaulting to desc.")  # noqa: E501
            ordering = 'desc'

        context['my_finished_growlogs'] = finished_growlogs
        context['my_finished_growlogs_sort'] = sort
        context['my_finished_growlogs_ordering'] = ordering
        return context

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name, self.get_context_data())


class MyGrowlogsView(HxMyActiveGrowlogsView, HxMyFinishedGrowlogsView, BaseView):
    template_name = GROW_TEMPLATES['grow/growlog/my_growlogs']

    def get_context_data(self, **kwargs):
        context = HxMyActiveGrowlogsView.get_context_data(
            self,
            **HxMyFinishedGrowlogsView.get_context_data(self, **kwargs)
        )
        context['finished_growlogs'] = Growlog.objects.filter(
            grower=self.request.user,
            finished_at__isnull=False
        ).order_by('name')
        return context

    def get(self, request: HttpRequest) -> HttpResponse:
        context = self.get_context_data()
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


class HxGrowlogAddSeedsStrainFilterView(LoginRequiredMixin, FormView):
    template_name = GROW_TEMPLATES['grow/growlog/growlog/hx/seeds_add']
    form_class = GrowlogSeedsFromStockForm

    def post(self, request: HttpRequest, growlog_pk: int) -> HttpResponse:
        self.growlog = get_object_or_404(Growlog, pk=growlog_pk)
        if not growlog_user_is_allowed_to_edit(request.user, self.growlog):
            raise PermissionDenied(_("You do not have permission to edit this growlog."))

        form = GrowlogSeedsFromStockForm(request.POST, user=request.user)
        # we want to run the validation to get the cleaned_data,
        # but we don't care if it's valid or not for this view
        form.is_valid()

        strain_filter = form.cleaned_data['strain_filter']
        if strain_filter:
            form.fields['seeds_in_stock'].queryset = StrainsInStock.objects.filter(
                user=request.user,
                strain__name__icontains=strain_filter
            ).order_by('strain__name', 'purchased_on')
        else:
            form.fields['seeds_in_stock'].queryset = StrainsInStock.objects.filter(
                user=request.user
            ).order_by('strain__name', 'purchased_on')

        return render(request, self.template_name, {
            'form': form,
            'growlog': self.growlog,
        })


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
        user_settings = GROW_USER_SETTINGS(self.request)

        active_growlogs = self.request.user.growlogs.filter(
            finished_at__isnull=True
        ).order_by('-started_at')

        paginate_by = self.request.GET.get(
            'active_growlogs_paginate_by',
            self.request.GET.get(
                'agl_paginate_by',
                self.request.GET.get(
                    'agl_pgn',
                    self.request.get(
                        'paginate_by',
                        self.request.get('pgn', user_settings.paginate)
                    )
                )
            )
        )
        page = self.request.GET.get(
            'active_growlogs_page',
            self.request.GET.get(
                'agl_page',
                self.request.GET.get(
                    self.request.GET.get(
                        'agl_p',
                        self.request.GET.get(
                            'page',
                            self.request.GET.get('p', 1)
                        )
                    )
                )
            )
        )

        paginator = QuerySetPaginator(
            reverse('grow:hx-growlog-active-info'),
            active_growlogs,
            paginate_by=paginate_by,
            page=page
        )

        context['active_growlogs_pagintor'] = paginator

        return context

    def get(self, request: HttpRequest, **kwargs) -> HttpResponse:
        return render(request, self.template_name, context=self.get_context_data())


class HxGrowlogFinishedInfoView(BaseView):
    template_name = GROW_TEMPLATES['grow/growlog/hx/finished_info']

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = dict(kwargs)

        user_settings = GROW_USER_SETTINGS(self.request)
        finished_growlogs = self.request.user.growlogs.filter(
            finished_at__isnull=False
        ).order_by('-finished_at')

        paginate_by = self.request.GET.get(
            'finished_growlogs_paginate_by',
            self.request.GET.get(
                'fgl_paginate_by',
                self.request.GET.get(
                    'fgl_pgn',
                    self.request.get(
                        'paginate_by',
                        self.request.get('pgn', user_settings.paginate)
                    )
                )
            )
        )
        page = self.request.GET.get(
            'finished_growlogs_page',
            self.request.GET.get(
                'fgl_page',
                self.request.GET.get(
                    'fgl_p',
                    self.request.GET.get(
                        'page',
                        1
                    )
                )
            )
        )

        paginator = QuerySetPaginator(
            reverse('grow:hx-growlog-finished-info'),
            finished_growlogs,
            paginate_by=paginate_by,
            page=page
        )

        context['finished_paginator'] = paginator

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

    hx_target = '#growlog-entries'
    update_page_url = True

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

    def form_valid(self, form):
        image = form.save(commit=False)
        image.growlog_entry = self.entry
        image.save()
        return redirect(reverse('grow:growlog-detail', kwargs={'pk': self.growlog.pk}))

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
        logger.info("Deleting image with id", self.image.id)

        self.image.image.delete(save=False)  # Delete the file from storage
        self.image.delete()
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        logger.error("Form invalid with errors: %s", form.errors)
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
            logger.error("Form invalid with errors: %s", form.errors)
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
