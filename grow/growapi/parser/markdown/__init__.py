import markdown
from django.utils.safestring import SafeString, mark_safe
from ... import settings


def render_markdown(text: str) -> SafeString:
    return mark_safe(markdown.markdown(text, extensions=settings.GROW_MARKDOWN_EXTENSIONS))


def render_description_markdown(text: str) -> SafeString:
    return mark_safe(markdown.markdown(text, extensions=settings.GROW_MARKDOWN_EXTENSIONS))
