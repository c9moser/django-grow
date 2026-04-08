from django.utils.translation import gettext as _
from .growapi import settings


class QuerySetPaginator:
    urlvars = {
        'paginate_by': 'paginate_by',
        'page': 'page',
    }

    def __init__(self,
                 base_url,
                 queryset,
                 paginate_by=10,
                 page=1):
        self.base_url = base_url
        self.queryset = queryset
        self.paginate_by = paginate_by
        self.current_page = page

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
                pages.append({
                    'page': i,
                    'current_page': i == self.current_page,
                    'text': str(i),
                    'url': f"{self.base_url}?{self.urlvars['page']}={i}&{self.urlvars['paginate_by']}={self.paginate_by}"
                })
        else:
            if self.current_page > 2:
                pages.append({
                    'page': 1,
                    'current_page': False,
                    'bs_icon': 'chevron-bar-left',
                    'text': _('First') if not settings.USE_BOOTSTRAP else '',
                    'url': f"{self.base_url}?{self.urlvars['page']}=1&{self.urlvars['paginate_by']}={self.paginate_by}"
                })
            if self.current_page > 1:
                pages.append({
                    'page': self.current_page - 1,
                    'current_page': False,
                    'bs_icon': 'chevron-left',
                    'text': _('Previous') if not settings.USE_BOOTSTRAP else '',
                    'url': f"{self.base_url}?{self.urlvars['page']}={self.current_page - 1}&{self.urlvars['paginate_by']}={self.paginate_by}"
                })

            pages.append({
                'page': self.current_page,
                'current_page': True,
                'text': str(self.current_page),
                'url': f"{self.base_url}?{self.urlvars['page']}={self.current_page}&{self.urlvars['paginate_by']}={self.paginate_by}"
            })

            if self.current_page < n_pages:
                pages.append({
                    'page': self.current_page + 1,
                    'current_page': False,
                    'bs_icon': 'chevron-right',
                    'text': _('Next') if not settings.USE_BOOTSTRAP else '',
                    'url': f"{self.base_url}?{self.urlvars['page']}={self.current_page + 1}&{self.urlvars['paginate_by']}={self.paginate_by}"
                })
            if self.current_page < n_pages - 1:
                pages.append({
                    'page': n_pages,
                    'current_page': False,
                    'bs_icon': 'chevron-bar-right',
                    'text': _('Last') if not settings.USE_BOOTSTRAP else '',
                    'url': f"{self.base_url}?{self.urlvars['page']}={n_pages}&{self.urlvars['paginate_by']}={self.paginate_by}"
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
