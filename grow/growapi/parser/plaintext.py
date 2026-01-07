from django.utils.safestring import SafeString, mark_safe
from django.utils.html import escape


def render_plaintext(text: str) -> SafeString:
    return mark_safe(f"<pre>{escape(text)}</pre>")
