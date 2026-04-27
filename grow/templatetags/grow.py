from django import template


register = template.Library()


@register.filter
def grow_urlencode(value: str) -> str:
    from urllib.parse import quote
    return quote(value)


@register.filter
def grow_template(template_name: str) -> str:
    from grow.settings import GROW_TEMPLATES

    return GROW_TEMPLATES.get(template_name, template_name)
