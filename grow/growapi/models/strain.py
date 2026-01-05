"""
Strain models
"""

from django.db import models
from django.db.models.functions import Upper
from django.utils.translation import gettext_lazy as _, get_language
from django.conf import settings as django_settings
from datetime import date

from ..enums import (
    TextType,
    TEXT_CHOICES,
    StrainType,
    STRAIN_TYPE_CHOICES
)

from ..parser.bbcode import render_description_bbcode
from ..parser.markdown import render_description_markdown


def get_language_code_choices():
    if hasattr(django_settings, 'LANGUAGES'):
        return [lang for lang in django_settings.LANGUAGES]
    else:
        return [
            ('de', _('German')),
            ('en-us', _("English (United States)"))
        ]


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

        if self.translations:
            translation = None
            try:
                translation = self.translations.get(language_code=get_language())
            except BreederTranslation.DoesNotExist:
                pass
            if not translation:
                try:
                    translation = self.translations.get(language_code=get_language().split('-')[0])
                except BreederTranslation.DoesNotExist:
                    pass

        if translation:
            print("USING TRANSLATION")
            description_type = translation.description_type
            description = translation.description if translation.description else self.description
        else:
            print("USING DEFAULT")
            description_type = self.description_type
            description = self.description

        if description:
            if description_type == TextType.BBCODE:
                return render_description_bbcode(description)
            elif description_type == TextType.MARKDOWN:
                return render_description_markdown(description)
            return description
        return ""

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
        django_settings.AUTH_USER_MODEL,
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

    moderator = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name=_("breeder moderator"),
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


class BreederTranslation(models.Model):
    breeder = models.ForeignKey(
        Breeder,
        on_delete=models.CASCADE,
        related_name="translations"
    )
    language_code = models.CharField(
        _("language code"),
        max_length=16,
        choices=get_language_code_choices()
    )

    description_type_data = models.CharField(
        _("description type"),
        max_length=50,
        default=TextType.MARKDOWN.value,
        choices=TEXT_CHOICES,
        db_column="description_type"
    )

    @property
    def description_type(self) -> TextType:
        return TextType.from_string(self.description_type_data)

    @description_type.setter
    def description_type(self, text_type: TextType | str):
        if not isinstance(text_type, TextType):
            text_type = TextType.from_string(text_type)
        self.description_type_data = text_type.value

    description = models.TextField(
        _("Description")
    )

    @property
    def description_html(self) -> str:
        if self.description_type == TextType.BBCODE:
            return mark_safe(render_description_bbcode(self.description))
        elif self.description_type == TextType.MARKDOWN:
            return render_description_markdown(self.description)
        else:
            return self.description

    class Meta:
        db_table = "grow_breeder_translation"
        unique_together = [
            ('language_code', 'breeder'),
        ]


class Strain(models.Model):
    breeder = models.ForeignKey(
        Breeder,
        on_delete=models.CASCADE,
        related_name="strains",
        verbose_name=_("breeder")
    )

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
        translation = None
        if self.translations:
            try:
                translation = self.translations.get(language_code=get_language())
            except StrainTranslation.DoesNotExist:
                pass
            if not translation:
                try:
                    translation = self.translations.get(language_code=get_language().split('-')[0])
                except StrainTranslation.DoesNotExist:
                    pass
        if translation:
            print("USING TRANSLATION")
            description_type = translation.description_type
            description = translation.description if translation.description else self.description
        else:
            print("USING DEFAULT")
            description_type = self.description_type
            description = self.description

        if description:
            if description_type == TextType.BBCODE:
                return render_description_bbcode(description)
            elif description_type == TextType.MARKDOWN:
                return render_description_markdown(description)
            return description
        return ""

    @property
    def description_type(self) -> TextType:
        return TextType.from_string(self.description_type_data)

    @description_type.setter
    def description_type(self, text_type: TextType | str):
        if not isinstance(text_type, TextType):
            text_type = TextType.from_string(text_type)
        self.description_type_data = text_type.value

    logo_url = models.URLField(
        _("logo url"),
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

    genotype_data = models.CharField(
        _("genotype"),
        max_length=127,
        choices=STRAIN_TYPE_CHOICES,
        default=StrainType.UNKNOWN.value,
        db_column="genotype",
    )

    created_by = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
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

    is_discontinued = models.BooleanField(
        _("is discontinued"),
        default=False
    )

    @property
    def genotype(self) -> StrainType:
        return StrainType.from_string(self.genotype_data)

    @genotype.setter
    def genotype(self, genetics: StrainType | str):
        if not isinstance(genetics, StrainType):
            genotype = StrainType.from_string(genetics)
        self.genotype_data = genotype.value

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

    def get_regular_seeds_in_stock(self, user) -> int:
        try:
            return self.seeds_in_stock.get(user=user, is_regular=True).quantity
        except StrainsInStock.DoesNotExist:
            return 0

    def get_feminized_seeds_in_stock(self, user) -> int:
        try:
            return self.seeds_in_stock.get(user=user, is_feminized=True).quantity
        except StrainsInStock.DoesNotExist:
            return 0

    def get_total_seeds_in_stock(self, user) -> int:
        return (self.get_feminized_seeds_in_stock(user)
                + self.get_regular_seeds_in_stock(user))

    def add_feminized_seeds_to_stock(self,
                                     user,
                                     quantity: int,
                                     purchased_on: date | None = None,
                                     notes: str = "",
                                     notes_type: TextType = TextType.MARKDOWN) -> int:

        if self.is_feminized:
            try:
                sis = self.seeds_in_stock.get(is_feminized=True, user=user)
                sis.quantity += quantity
                if notes:
                    sis.notes = notes
                    sis.notes_type = notes_type
                if purchased_on is not None:
                    sis.purchased_on = purchased_on
                sis.save()

            except StrainsInStock.DoesNotExist:
                sis = StrainsInStock.objects.create(
                    strain=self,
                    user=user,
                    quantity=quantity,
                    is_feminized=True,
                    is_regular=False,
                    purchased_on=purchased_on,
                    notes=notes,
                    notes_type=notes_type
                )
            return sis.quantity
        return 0

    def remove_feminized_seeds_from_stock(self,
                                          user,
                                          quantity: int) -> int:
        if self.is_feminized:
            try:
                sis = self.seeds_in_stock.get(is_feminized=True, user=user)
                if sis.quantity > quantity:
                    sis.quantity -= quantity
                else:
                    sis.quantity = 0
                if sis.quantity == 0:
                    sis.purchased_on = None
                sis.save()
                return sis.quantity
            except StrainsInStock.DoesNotExist:
                pass
        return 0

    def add_regular_seeds_to_stock(self,
                                   user,
                                   quantity: int,
                                   purchased_on: date | None = None,
                                   notes: str = "",
                                   notes_type: TextType = TextType.MARKDOWN) -> int:

        if self.is_regular:
            try:
                sis = self.seeds_in_stock.get(is_regular=True, user=user)
                sis.quantity += quantity
                if notes:
                    sis.notes = notes
                    sis.notes_type = notes_type
                if purchased_on is not None:
                    sis.purchased_on = purchased_on
                sis.save()

            except StrainsInStock.DoesNotExist:
                sis = StrainsInStock.objects.create(
                    strain=self,
                    user=user,
                    quantity=quantity,
                    purchased_on=purchased_on,
                    is_feminized=False,
                    is_regular=True,
                    notes=notes,
                    notes_type=notes_type
                )
            return sis.quantity
        return 0

    def remove_regualar_seeds_from_stock(self,
                                         user,
                                         quantity: int) -> int:
        print("REMOVE REGULAR SEEDS")
        if self.is_regular:
            try:
                sis = self.seeds_in_stock.get(is_regular=True, user=user)
                if sis.quantity > quantity:
                    sis.quantity -= quantity
                else:
                    sis.quantity = 0
                if sis.quantity == 0:
                    sis.purchased_on = None
                sis.save()
                return sis.quantity
            except StrainsInStock.DoesNotExist:
                pass
        return 0

    def get_feminized_seeds_purchased_on(self, user):
        try:
            sis = self.seeds_in_stock.get(user=user, is_feminized=True)
            if sis.quantity > 0:
                return sis.purchased_on
            return None
        except StrainsInStock.DoesNotExist:
            return None

    def get_regular_seeds_purchased_on(self, user):
        try:
            sis = self.seeds_in_stock.get(user=user, is_regular=True)
            if sis.quantity > 0:
                return sis.purchased_on
            return None
        except StrainsInStock.DoesNotExist:
            return None

    def __str__(self):
        return f"{self.breeder.name} - {self.name}"

    class Meta:
        db_table = "grow_strain"
        unique_together = [
            ('slug', 'breeder'),
            ('name', 'breeder'),
        ]
        ordering = ['breeder__name', 'name']


class StrainTranslation(models.Model):
    strain = models.ForeignKey(
        Strain,
        on_delete=models.CASCADE,
        verbose_name=_("strain"),
        related_name="translations"
    )
    language_code = models.CharField(
        _("Language code"),
        max_length=16,
        choices=get_language_code_choices()
    )
    description_type_data = models.CharField(
        _("description type"),
        max_length=50,
        default=TextType.MARKDOWN.value,
        choices=TEXT_CHOICES,
        db_column="description_type"
    )

    @property
    def description_type(self) -> TextType:
        return TextType.from_string(self.description_type_data)

    @description_type.setter
    def description_type(self, text_type: TextType | str):
        if not isinstance(text_type, TextType):
            text_type = TextType.from_string(text_type)
        self.description_type_data = text_type.value

    description = models.TextField(
        _("description")
    )

    class Meta:
        db_table = "grow_strain_translation"
        unique_together = [
            ('language_code', 'strain')
        ]


class StrainUserComment(models.Model):
    strain = models.ForeignKey(
        Strain,
        on_delete=models.CASCADE,
        related_name="user_comments",
        verbose_name=_("strain")
    )
    language_code = models.CharField(


    )
    user = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='strain_comments',
        verbose_name=_("user"),
    )
    comment = models.TextField(
        _("comment"))
    comment_type_data = models.CharField(
        _("description type"),
        max_length=50,
        default=TextType.MARKDOWN.value,
        choices=TEXT_CHOICES,
        db_column="comment_type"
    )

    @property
    def comment_type(self) -> TextType:
        return TextType.from_string(self.comment_type_data)

    @comment_type.setter
    def comment_type(self, text_type: TextType | str):
        if not isinstance(text_type, TextType):
            text_type = TextType.from_string(text_type)
        self.comment_type_data = text_type.value

    created_at = models.DateTimeField(
        _("created at"),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _("updated at"),
        auto_now=True
    )

    class Meta:
        db_table = "grow_strain_user_comment"
        unique_together = [
            ('strain', 'user'),
        ]


class StrainImage(models.Model):
    strain = models.ForeignKey(
        Strain,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("user description"),
    )
    user = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
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

    caption = models.CharField(
        _("caption"),
        max_length=255,
        null=True,
        blank=True
    )

    @property
    def description_type(self) -> TextType:
        return TextType.from_string(self.description_type_data)

    @description_type.setter
    def description_type(self, text_type: TextType | str):
        if not isinstance(text_type, TextType):
            text_type = TextType.from_string(text_type)
        self.description_type_data = text_type.value

    class Meta:
        db_table = "grow_strain_image"


class StrainsInStock(models.Model):
    strain = models.ForeignKey(Strain,
                               on_delete=models.CASCADE,
                               related_name="seeds_in_stock",
                               verbose_name=_("strain"))
    user = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='seeds_in_stock',
        verbose_name=_("user"),
    )
    is_regular = models.BooleanField(
        _("regular seeds"),
        default=False
    )
    is_feminized = models.BooleanField(
        _("feminized seeds"),
        default=True
    )

    quantity = models.IntegerField(
        _("quantity"),
        default=0
    )
    purchased_on = models.DateField(
        _("purchased on"),
        blank=True,
        null=True
    )
    notes = models.TextField(
        _("notes"),
        blank=True,
        null=True
    )
    notes_type_data = models.CharField(
        _("text type"),
        max_length=50,
        choices=TEXT_CHOICES,
        default=TextType.MARKDOWN.value,
        db_column="notes_type",
    )

    @property
    def notes_type(self) -> TextType:
        return TextType.from_string(self.notes_type_data)

    @notes_type.setter
    def notes_type(self, text_type: TextType | str):
        if not text_type:
            text_type = TextType.MARKDOWN
        elif not isinstance(text_type, TextType):
            text_type = TextType.from_string(text_type)
        self.notes_type_data = text_type.value

    class Meta:
        db_table = "grow_strains_in_stock"

        unique_together = [
            ('strain', 'user', 'is_feminized'),
        ]

        constraints = [
            # Check that is_feminized or is_regular is set
            models.CheckConstraint(
                name="strainsinstock_one_of_regular_feminized_set",
                condition=(models.Q(is_regular=True) | models.Q(is_feminized=True))
            ),
        ]

        ordering = ['strain__breeder__name', 'strain__name', 'is_feminized']
