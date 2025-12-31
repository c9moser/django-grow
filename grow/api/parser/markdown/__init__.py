import markdown
from django.utils.safestring import SafeString, mark_safe


def reander_markdown(text: str) -> SafeString:
    return mark_safe(markdown.markdown(text))


def render_description_markdown(text: str) -> SafeString:
    return mark_safe(markdown.markdown(text))
