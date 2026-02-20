from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class GrowUserSettings(models.Model):
    """
    User settings for grow.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='grow_settings',
        verbose_name=_("user"),
    )

    growlog_paginate = models.IntegerField(
        _("growlog paginate"),
        default=20,
    )

    paginate = models.IntegerField(
        _("paginate"),
        default=25,
    )

    class Meta:
        verbose_name = _("grow setting")
        verbose_name_plural = _("grow settings")
        db_table = "grow_user_settings"
