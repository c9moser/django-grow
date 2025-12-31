from ... import settings

from .text_formatters import (
    render_codeblock,
    render_url,
    render_list_item,
    render_ordered_list,
    render_unordered_list,
    render_paragraph,
    render_image,
    render_wiki_image,
    render_wiki_link,
    render_wiki_url,
    render_table,
    render_table_header,
    render_table_data,
    render_table_row,
    render_youtube_video,
)

from .simple_formatters import (  # noqa: F401
    SIMPLE_FORMATTERS,
    SIMPLE_DESCRIPTION_FORMATTERS,
)
# a list of tuples containig an tuple args and a dict of kwargs

# a list of tuples containing an tuple of args and a dict of kwargs
FORMATTERS = [
    (
        ('url', render_url),
        {
            'strip': True,
            'swallow_trailing_newline': True,
            'same_tag_closes': True
        }
    ),
    (
        ('wiki', render_wiki_link),
        {
            'strip': True,
            'swallow_tailin_newline': True,
            'standalone': True
        }
    ),
    (
        ('codeblock', render_codeblock),
        {
            'strip': True,
            'swallow_trailing_newline': False,
            'same_tag_closes': False,
            'render_embedded': False
        }
    ),
    (('ol', render_ordered_list), {}),
    (('ul', render_unordered_list), {}),
    (('li', render_list_item), {}),
    (('p', render_paragraph), {'same_tag_closes': False}),
    (('image', render_image), {'same_tag_closes': True}),
    (('img', render_image), {'same_tag_closes': True}),
    (('wiki-image', render_wiki_image), {'standalone': True}),
    (('wimg', render_wiki_image), {'standalone': True}),
    (('table', render_table), {}),
    (('table-row', render_table_row), {}),
    (('tr', render_table_row), {}),
    (('table-header', render_table_header), {}),
    (('th', render_table_header), {}),
    (('table-data', render_table_data), {}),
    (('td', render_table_data), {}),
    (('youtube', render_youtube_video), {'same_tag_closes': True}),
]


DESCRIPTION_FORMATTERS = [
    (
        ('url', render_url),
        {
            'strip': True,
            'swallow_trailing_newline': True,
            'same_tag_closes': True
        }
    ),
    (
        ('codeblock', render_codeblock),
        {
            'strip': True,
            'swallow_trailing_newline': False,
            'same_tag_closes': False,
            'render_embedded': False
        }
    ),
    (('ol', render_ordered_list), {}),
    (('ul', render_unordered_list), {}),
    (('li', render_list_item), {}),
    (('p', render_paragraph), {'same_tag_closes': False}),
    (('image', render_image), {'same_tag_closes': True}),
    (('img', render_image), {'same_tag_closes': True}),
    (('table', render_table), {}),
    (('table-row', render_table_row), {}),
    (('tr', render_table_row), {}),
    (('table-header', render_table_header), {}),
    (('th', render_table_header), {}),
    (('table-data', render_table_data), {}),
    (('td', render_table_data), {}),
    (('youtube', render_youtube_video), {'same_tag_closes': True}),
]

if settings.INCLUDE_WIKI:
    FORMATTERS += [
        (
            ('wiki-url', render_wiki_url),
            {
                'strip': True,
                'swallow_trailing_newline': True,
                'same_tag_closes': True
            }
        ),
        (
            ('wiki', render_wiki_link),
            {
                'strip': True,
                'swallow_tailin_newline': True,
                'standalone': True
            }
        ),
        (('wiki-image', render_wiki_image), {'standalone': True}),
        (('wimg', render_wiki_image), {'standalone': True}),
    ]
    DESCRIPTION_FORMATTERS += [
        (
            ('wiki-url', render_wiki_url),
            {
                'strip': True,
                'swallow_trailing_newline': True,
                'same_tag_closes': True
            }
        ),
        (
            ('wiki', render_wiki_link),
            {
                'strip': True,
                'swallow_tailin_newline': True,
                'standalone': True
            }
        ),
        (('wiki-image', render_wiki_image), {'standalone': True}),
        (('wimg', render_wiki_image), {'standalone': True}),
    ]
