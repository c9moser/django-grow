"""
Strain models
"""

from django.db import models
from django.db.models.functions import Upper
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from ..enums import (
    TextType,
    TEXT_CHOICES,
    StrainType,
    STRAIN_TYPE_CHOICES
)

from ..parser.bbcode import render_description_bbcode
from ..parser.markdown import render_description_markdown


class Breeder(models.Model):
    slug = models.SlugField(
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

    @property
    def description_html(self) -> str:
        if not self.description:
            return ""

        if self.description_type == TextType.BBCODE:
            return render_description_bbcode(self.description)
        elif self.description_type == TextType.MARKDOWN:
            return render_description_markdown(self.description)
        else:
            return self.description

    @property
    def has_description(self) -> bool:
        return bool(self.description)

    description_type_data = models.CharField(
        _("description type"),
        max_length=50,
        default=TextType.MARKDOWN.value,
        db_column="description_type",
        choices=TEXT_CHOICES
    )

    logo_url = models.URLField(
        _("logo URL"),
        blank=True,
        null=True
    )

    logo_image = models.ImageField(
        _("logo image"),
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
        _("breeder url"),
        blank=True,
        null=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='breeders',
        verbose_name=_("owner"),
    )

    creator_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    added_at = models.DateTimeField(
        _("added at"),
        auto_now_add=True
    )

    @property
    def description_type(self):
        return TextType.from_string(self.description_type_data)

    @description_type.setter
    def description_type(self, text_type: TextType | str):
        if not isinstance(text_type, TextType):
            text_type = TextType.from_string(TextType)
        self.description_type_data = text_type.value

    @property
    def strains_sorted(self):
        return self.strains.all().order_by(Upper('name'))

    @property
    def strain_count(self) -> int:
        return self.strains.count()

    @property
    def growlog_count(self) -> int:
        if self.strain_count > 0:
            return sum(strain.growlog_count for strain in self.strains.all())
        return 0

    @property
    def strains_with_growlogs(self):
        ret = []
        for strain in self.strains.all():
            if strain.growlog_count > 0:
                ret.append(strain)

    @property
    def strains_with_growlogs_count(self) -> int:
        ret = 0
        for strain in self.strains.all():
            if strain.growlog_count > 0:
                ret += 1
        return ret

    @property
    def has_logo(self) -> bool:
        return (bool(self.logo_image) or bool(self.logo_url))

    @property
    def logo(self) -> str:
        """
        Returns the image url if logo_image.url or logo_url exists.
        If none of both exist an empty string is returned.

        :return: The logo image url.
        :rtype: str
        """
        if self.logo_image:
            return self.logo_image.url
        if self.logo_url:
            return self.logo_url
        return ""

    def __str__(self):
        return self.name

    class Meta:
        db_table = "grow_breeder"
        ordering = ['name']


class Strain(models.Model):
    slug = models.SlugField(
        _("key"),
        max_length=255
    )
    name = models.CharField(
        _("strain name"),
        max_length=255
    )
    description = models.TextField(
        _("description"),
        blank=True,
        null=True
    )
    description_type_data = models.CharField(
        _("description type"),
        max_length=50,
        default=TextType.MARKDOWN.value,
        choices=TEXT_CHOICES,
        db_column="description_type"
    )

    @property
    def has_description(self) -> bool:
        return bool(self.description)

    @property
    def description_html(self):
        if not self.description:
            return ""

        if self.description_type == TextType.BBCODE:
            return render_description_bbcode(self.description)
        elif self.description_type == TextType.MARKDOWN:
            return render_description_markdown(self.description)

        return self.description

    @property
    def description_type(self) -> TextType:
        return TextType.from_string(self.description_type_data)

    @description_type.setter
    def description_type(self, text_type: TextType | str):
        if not isinstance(text_type, TextType):
            text_type = TextType.from_string(text_type)

        self.description_type_data = text_type.value

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

    logo_image = models.ImageField(
        _("logo image"),
        upload_to='grow/strain/logos/',
        blank=True,
        null=True
    )

    strain_url = models.URLField(
        _("strain homepage"),
        null=True,
        blank=True
    )

    seedfinder_url = models.URLField(
        _("seedfinder url"),
        null=True,
        blank=True
    )

    is_automatic = models.BooleanField(
        _("is automatic"),
        default=False
    )
    is_feminized = models.BooleanField(
        _("is feminized"),
        default=True
    )
    is_regular = models.BooleanField(
        _("is regular"),
        default=False
    )

    flowering_time_days = models.IntegerField(
        _("flowering time (days)"),
        default=0
    )

    genetics_data = models.CharField(
        _("strain type"),
        max_length=127,
        choices=STRAIN_TYPE_CHOICES,
        default=StrainType.UNKNOWN.value,
        db_column="genetics",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="strains",
        verbose_name=_("created by")
    )
    creator_name = models.CharField(
        _("The name of the creator"),
        max_length=255,
        null=True,
        blank=True
    )
    added_at = models.DateTimeField(
        _("added at"),
        auto_now_add=True,
    )

    @property
    def genetics(self) -> StrainType:
        return StrainType.from_string(self.genetics_data)

    @genetics.setter
    def genetics(self, genetics: StrainType):
        self.genetics_data = genetics.value

    @property
    def growlog_count(self):
        return self.growlog_strains.count()

    @property
    def flowering_time_weeks(self) -> int:
        if not self.flowering_time_days:
            return 0

        ret = self.flowering_time_days // 7
        if (self.flowering_time_days % 7) > 3:
            ret += 1
        return ret

    @property
    def has_logo(self) -> bool:
        return (bool(self.logo_image) or bool(self.logo_url))

    @property
    def logo(self) -> str:
        if self.logo_image:
            return self.logo_image.url
        elif self.logo_url:
            return self.logo_url
        return ""

    class Meta:
        db_table = "grow_strain"
        unique_together = ('slug', 'breeder')
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

    uplaoder_name = models.CharField(
        _("uploader"),
        max_length=255,
        null=True,
        blank=True,
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

    @property
    def description_type(self) -> TextType:
        return TextType.from_string(self.description_type_data)

    @description_type.setter
    def description_type(self, description_type: TextType):
        self.description_type_data = description_type.value

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
