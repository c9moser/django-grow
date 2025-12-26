"""
Strain models
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from ..enums import (
    TextType,
    TEXT_CHOICES,
    StrainType,
    STRAIN_TYPE_CHOICES
)


class Breeder(models.Model):
    key = models.SlugField(
        _("key"),
        max_length=255,
        unique=True
    )
    name = models.CharField(
        _("name"),
        max_length=255
    )
    description = models.TextField(
        _("description"),
        blank=True,
        null=True
    )
    description_type = models.CharField(
        _("description type"),
        max_length=50,
        default="markdown",
        choices=TEXT_CHOICES
    )

    logo_url = models.URLField(
        _("logo URL"),
        blank=True,
        null=True
    )
    logo_icon = models.ImageField(
        _("logo icon"),
        upload_to='grow/breeder_logos/',
        blank=True,
        null=True
    )

    seedfinder_url = models.URLField(
        _("Seedfinder URL"),
        blank=True,
        null=True
    )

    breeder_url = models.URLField(
        _("breeder URL"),
        blank=True,
        null=True
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='breeders',
        verbose_name=_("owner"),
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = "grow_breeder"
        ordering = ['name']


class Strain(models.Model):
    key = models.SlugField(
        _("key"),
        max_length=255
    )
    name = models.CharField(
        _("name"),
        max_length=255
    )
    description = models.TextField(
        _("description"),
        blank=True,
        null=True
    )
    description_type = models.CharField(
        _("description type"),
        max_length=50,
        default="markdown",
        choices=TEXT_CHOICES
    )
    breeder = models.ForeignKey(
        Breeder,
        on_delete=models.CASCADE,
        related_name="strains",
        verbose_name=_("breeder")
    )

    logo_url = models.URLField(
        _("logo URL"),
        blank=True,
        null=True
    )

    logo = models.ImageField(
        _("logo"),
        upload_to='grow/strain/logos/',
        blank=True,
        null=True
    )

    is_automatic = models.BooleanField(
        _("is automatic"),
        default=False
    )
    is_feminized = models.BooleanField(
        _("is feminized"),
        default=True
    )
    flowering_time_days = models.IntegerField(
        _("flowering time (days)"),
        default=0
    )
    strain_type = models.CharField(
        _("strain type"),
        max_length=50,
        choices=STRAIN_TYPE_CHOICES,
        default=StrainType.HYBRID.value
    )

    class Meta:
        db_table = "grow_strain"
        unique_together = ('key', 'breeder')
        ordering = ['breeder__name', 'name']

    def __str__(self):
        return f"{self.breeder.name} - {self.name}"


class StrainUserComments(models.Model):
    strain = models.ForeignKey(
        Strain,
        on_delete=models.CASCADE,
        related_name="user_comments",
        verbose_name=_("strain")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='strain_comments',
        verbose_name=_("user"),
    )
    comment = models.TextField(
        _("comment"))
    comment_type = models.CharField(
        _("description type"),
        max_length=50,
        default="markdown",
        choices=TEXT_CHOICES
    )

    created_at = models.DateTimeField(
        _("created at"),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _("updated at"),
        auto_now=True
    )

    class Meta:
        db_table = "grow_strain_user_description"
        unique_together = ('strain', 'user')


class StrainImage(models.Model):
    strain = models.ForeignKey(
        Strain,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("user description"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="strain_images",
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        editable=False,
    )
    image = models.ImageField(
        _("image"),
        upload_to='grow/strain/user_images/'
    )

    uploaded_at = models.DateTimeField(
        _("uploaded at"),
        auto_now_add=True
    )

    description = models.TextField(
        _("description"),
        null=True,
        blank=True
    )

    description_type_data = models.CharField(
        _("description"),
        max_length=50,
        default=TextType.MARKDOWN.value,
        choices=TEXT_CHOICES
    )

    class Meta:
        db_table = "grow_strain_image"


class StrainsInStock(models.Model):
    strain = models.ForeignKey(Strain,
                               on_delete=models.CASCADE,
                               related_name="stocks",
                               verbose_name=_("strain"))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='strains_in_stock',
        verbose_name=_("user"),
    )
    quantity = models.IntegerField(_("quantity"),
                                   default=0)
    bought_at = models.DateField(_("bought at"),
                                 blank=True,
                                 null=True)
    notes = models.TextField(_("notes"),
                             blank=True,
                             null=True)

    class Meta:
        db_table = "grow_strains_in_stock"
        unique_together = ('strain', 'user')
