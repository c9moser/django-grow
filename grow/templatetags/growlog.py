from django import template
from django.http import HttpRequest
from django.utils.safestring import SafeString, mark_safe
from django.utils.translation import ngettext, gettext as _
from django.template.loader import render_to_string
from grow.growapi.models import GrowlogEntry
from grow.growapi.permission import growlog_user_is_allowed_to_edit


register = template.Library()


@register.filter
def growlog_entry_timestamp(entry: GrowlogEntry, request: HttpRequest) -> SafeString | str:
    if growlog_user_is_allowed_to_edit(request.user, entry.growlog):

        return mark_safe(
            render_to_string(
                "grow/growlog/entry/timestamp.html",
                {"entry": entry}
            )
        )
    else:
        years, weeks, days = entry.duration_years_weeks_days
        parts = []
        if years:
            parts.append(ngettext("{n} year", "{n} years", years).format(n=years))
        if weeks:
            parts.append(ngettext("{n} week", "{n} weeks", weeks).format(n=weeks))
        if days:
            parts.append(ngettext("{n} day", "{n} days", days).format(n=days))

        if parts:
            ret = ", ".join(parts)
        else:
            ret = _("0 days")

        ts = entry.timestamp
        ret += f" {ts.hour:02d}:{ts.minute:02d}:{ts.second:02d}"

        return ret
