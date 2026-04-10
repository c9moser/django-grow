from django.utils.translation import gettext as _
from django.urls import reverse
from .growapi import settings


class QuerySetPaginator:
    urlvars = {
        'paginate_by': 'paginate_by',
        'page': 'page',
    }

    def __init__(self,
                 queryset,
                 base_url=None,
                 url_path=None,
                 url_path_kwargs=None,
                 url_variables=None,
                 paginate_by=10,
                 page=1):
        self.base_url = base_url
        self.url_path = url_path
        self.url_path_kwargs = url_path_kwargs if url_path_kwargs is not None else {}
        self._url_variables = url_variables if url_variables is not None else {}
        self.queryset = queryset

        if not url_path and not base_url:
            raise ValueError("Either base_url or url_path must be provided.")

        try:
            self.paginate_by = int(paginate_by)
        except (ValueError, TypeError):
            self.paginate_by = 10
        try:
            self.current_page = int(page)
        except (ValueError, TypeError):
            self.current_page = 1

    @property
    def n_pages(self):
        n_items = self.queryset.count() if hasattr(self.queryset, 'count') else len(self.queryset)

        if self.paginate_by <= 0:
            return 1

        n_pages = (n_items + self.paginate_by - 1) // self.paginate_by

        return max(n_pages, 1)

    @property
    def page_range(self):
        return range(1, self.n_pages + 1)

    @property
    def page(self):
        n_pages = self.n_pages
        if self.current_page == -1:
            self.current_page = n_pages
        elif self.current_page < 1:
            self.current_page = 1
        elif self.current_page > n_pages:
            self.current_page = n_pages

        return self.queryset[(self.current_page - 1) * self.paginate_by:
                             self.current_page * self.paginate_by]

    @property
    def pagination(self):
        n_pages = self.n_pages
        pages = []

        if n_pages < 6:
            for i in range(1, n_pages + 1):
                vars = dict(self.url_variables)
                vars[self.urlvars['page']] = i
                vars[self.urlvars['paginate_by']] = self.paginate_by

                if self.url_path:
                    url = reverse(self.url_path, kwargs=self.url_path_kwargs, query=vars)
                else:
                    url_vars = '&'.join([f"{key}={value}" for key, value in vars.items()])
                    url = f"{self.base_url}?{url_vars}"

                pages.append({
                    'page': i,
                    'current_page': i == self.current_page,
                    'text': str(i),
                    'url': url
                })
        else:
            if self.current_page > 2:
                url_vars = dict(self.url_variables)
                url_vars[self.urlvars['page']] = 1
                url_vars[self.urlvars['paginate_by']] = self.paginate_by
                if self.url_path:
                    url = reverse(self.url_path, kwargs=self.url_path_kwargs, query=url_vars)
                else:
                    url_vars_str = '&'.join([f"{key}={value}" for key, value in url_vars.items()])
                    url = f"{self.base_url}?{url_vars_str}"

                pages.append({
                    'page': 1,
                    'current_page': False,
                    'bs_icon': 'chevron-bar-left',
                    'text': _('First') if not settings.USE_BOOTSTRAP else '',
                    'url': url
                })
            if self.current_page > 1:
                url_vars = dict(self.url_variables)
                url_vars[self.urlvars['page']] = self.current_page - 1
                url_vars[self.urlvars['paginate_by']] = self.paginate_by

                if self.url_path:
                    url = reverse(self.url_path, kwargs=self.url_path_kwargs, query=url_vars)
                else:
                    url_vars_str = '&'.join([f"{key}={value}" for key, value in url_vars.items()])
                    url = f"{self.base_url}?{url_vars_str}"

                pages.append({
                    'page': self.current_page - 1,
                    'current_page': False,
                    'bs_icon': 'chevron-left',
                    'text': _('Previous') if not settings.USE_BOOTSTRAP else '',
                    'url': url,
                })

            pages.append({
                'page': self.current_page,
                'current_page': True,
                'text': str(self.current_page),
                'url': self.url
            })

            if self.current_page < n_pages:
                url_vars = dict(self.url_variables)
                url_vars[self.urlvars['page']] = self.current_page + 1
                url_vars[self.urlvars['paginate_by']] = self.paginate_by

                if self.url_path:
                    url = reverse(self.url_path, kwargs=self.url_path_kwargs, query=url_vars)
                else:
                    url_vars_str = '&'.join([f"{key}={value}" for key, value in url_vars.items()])
                    url = f"{self.base_url}?{url_vars_str}"

                pages.append({
                    'page': self.current_page + 1,
                    'current_page': False,
                    'bs_icon': 'chevron-right',
                    'text': _('Next') if not settings.USE_BOOTSTRAP else '',
                    'url': url,
                })

            if self.current_page < n_pages - 1:
                url_vars = dict(self.url_variables)
                url_vars[self.urlvars['page']] = n_pages
                url_vars[self.urlvars['paginate_by']] = self.paginate_by

                if self.url_path:
                    url = reverse(self.url_path, kwargs=self.url_path_kwargs, query=url_vars)
                else:
                    url_vars_str = '&'.join([f"{key}={value}" for key, value in url_vars.items()])
                    url = f"{self.base_url}?{url_vars_str}"

                pages.append({
                    'page': n_pages,
                    'current_page': False,
                    'bs_icon': 'chevron-bar-right',
                    'text': _('Last') if not settings.USE_BOOTSTRAP else '',
                    'url': url,
                })

        return pages

    @property
    def get_paginator_context_data(self):
        return {
            'current_page': self.current_page,
            'paginate_by': self.paginate_by,
            'n_pages': self.n_pages,
            'page_range': self.page_range,
            'paginator': self,
        }

    @property
    def url(self):
        vars = dict(self.url_variables)
        vars[self.urlvars['page']] = self.current_page
        vars[self.urlvars['paginate_by']] = self.paginate_by

        if self.url_path:
            url = reverse(self.url_path, kwargs=self.url_path_kwargs, query=vars)
        else:
            url_vars= '&'.join([f"{key}={value}" for key, value in vars.items()])
            url = f"{self.base_url}?{url_vars}"

        return url

    @property
    def url_variables(self):
        ret = dict(self._url_variables)
        ret[self.urlvars['page']] = self.current_page
        ret[self.urlvars['paginate_by']] = self.paginate_by
        return ret
