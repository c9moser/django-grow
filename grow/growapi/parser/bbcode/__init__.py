import bbcode
from . import formatters
from django.utils.safestring import mark_safe


PARSER = bbcode.Parser(newline="\n", escape_html=True, replace_links=False)
DESCRIPTION_PARSER = bbcode.Parser(newline="\n", escape_html=True, replace_links=False)


def create_formatters(parser, simple_formatters, text_formatters):
    for i in simple_formatters:
        if len(i) == 0:
            continue

        if len(i) == 1:
            kwargs = {}
        else:
            kwargs = i[1]
        parser.add_simple_formatter(*i[0], **kwargs)

    for i in text_formatters:
        if len(i) == 0:
            continue

        if len(i) == 1:
            kwargs = {}
        else:
            kwargs = i[1]

        print(f"Adding formatter: {i[0][0]} with kwargs: {kwargs}")

        parser.add_formatter(*i[0], **kwargs)


create_formatters(PARSER,
                  formatters.SIMPLE_FORMATTERS,
                  formatters.FORMATTERS)
create_formatters(DESCRIPTION_PARSER,
                  formatters.SIMPLE_DESCRIPTION_FORMATTERS,
                  formatters.DESCRIPTION_FORMATTERS)


def render_bbcode(text: str):
    return mark_safe(PARSER.format(text))


def render_description_bbcode(text: str):
    return mark_safe(DESCRIPTION_PARSER.format(text))
