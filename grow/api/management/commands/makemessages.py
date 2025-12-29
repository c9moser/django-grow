from django.core.management.commands.makemessages import Command as BaseCommand


class Command(BaseCommand):
    help = (
        BaseCommand.help +
        "Extends extraction of the N_(message) for gettext_noop, "
        "X_(singular,plural,n) for ngettext "
        "L_(message) for gettext_lazy and Q_(message) pgettext keys."
    )

    xgettext_options = BaseCommand.xgettext_options + ['-kN_:1', '-kQ_:2', '-kL_:1', "-kX_:1,2"]
