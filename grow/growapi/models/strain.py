"""
Strain models
"""

from typing import Union
from django.db import models
from django.db.models.functions import Upper
from django.utils.translation import gettext_lazy as _, get_language
from django.utils.safestring import SafeString


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
from ..parser.plaintext import render_plaintext


def get_language_code_choices():
    if hasattr(django_settings, 'LANGUAGES'):
        return [lang for lang in django_settings.LANGUAGES]
    else:
        return [
            ('de', _('German')),
            ('en-us', _("English (United States)"))
        ]


class Breeder(models.Model):
    """Breeder model"""

    #: The unique slug/key of the breeder
    #:
    #: Used to identify the breeder in URLs and API calls
    #:
    #: :type: str
    slug = models.SlugField(
        _("key"),
        max_length=255,
        unique=True
    )

    #: The name of the breeder
    #:
    #: Can be translated using the BreederTranslation model
    #:
    #: :type: str
    name = models.CharField(
        _("name"),
        max_length=255
    )

    @property
    def locale_name(self) -> str:
        """
        The localized name of the breeder.

        This property checks for translations first and falls back to the default
        name if no translation is found.

        :return: The localized name.
        :rtype: str
        """

        if self.translations:
            try:
                translation = self.translations.get(language_code=get_language())
                if translation.name:
                    return translation.name
            except BreederTranslation.DoesNotExist:
                pass

            try:
                translation = self.translations.get(language_code=get_language().split('-')[0])
                if translation.name:
                    return translation.name
            except BreederTranslation.DoesNotExist:
                pass

        return self.name

    #: The description of the breeder
    #: Can be translated using the BreederTranslation model
    #: :type: str
    description = models.TextField(
        _("description"),
        blank=True,
        null=True
    )

    @property
    def description_html(self) -> SafeString | str:
        """
        The HTML rendered description of the breeder.

        :return: The HTML rendered description.
        :rtype: SafeString | str
        """
        if self.description_type == TextType.BBCODE:
            return render_description_bbcode(self.description)
        elif self.description_type == TextType.MARKDOWN:
            return render_description_markdown(self.description)
        elif self.description_type == TextType.PLAIN:
            return render_plaintext(self.description)
        else:
            return self.description

    @property
    def locale_description_html(self) -> SafeString | str:
        """
        The HTML rendered description of the breeder.

        This property checks for translations first and falls back to the default
        description if no translation is found.

        :return: The HTML rendered description.
        :rtype: str
        """

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
        """
        Checks if the breeder has a description set.

        :return: True if a description exists, False otherwise.
        :rtype: {% if 'website' in form.errors %}
            bool
        """
        try:
            translation = self.translations.get(language_code=get_language())
            if translation.description:
                return True
        except BreederTranslation.DoesNotExist:
            pass

        try:
            translation = self.translations.get(language_code=get_language().split('-')[0])
            if translation.description:
                return True
        except BreederTranslation.DoesNotExist:
            pass

        if self.description:
            return True
        return False

    #: The type of the description text
    #: #: :type: TextType
    description_type_data = models.CharField(
        _("description type"),
        max_length=50,
        default=TextType.MARKDOWN.value,
        db_column="description_type",
        choices=TEXT_CHOICES
    )

    #: The logo URL of the breeder
    #: :type: str
    logo_url = models.URLField(
        _("logo URL"),
        blank=True,
        null=True
    )

    #: The logo image of the breeder
    #: :type: ImageField
    logo_image = models.ImageField(
        _("logo image"),
        upload_to='grow/breeder_logos/',
        blank=True,
        null=True
    )

    #: The Seedfinder URL of the breeder
    #: :type: str
    seedfinder_url = models.URLField(
        _("Seedfinder URL"),
        blank=True,
        null=True
    )

    @property
    def locale_seedfinder_url(self) -> str | None:
        """
        Get the localized Seedfinder URL for the breeder.

        If a translation exists for the current language, it returns the translated URL.
        Otherwise, it falls back to the default Seedfinder URL.

        :return: The localized Seedfinder URL or the default URL.
        :rtype: str | None
        """
        translation = None
        if self.translations:
            try:
                translation = self.translations.get(language_code=get_language())
            except BreederTranslation.DoesNotExist:
                pass
            if not translation:
                try:
                    translation = self.translations.get(language_code=get_language().split('-')[0])
                except BreederTranslation.DoesNotExist:
                    pass
        if translation and translation.seedfinder_url:
            return translation.seedfinder_url
        return self.seedfinder_url

    #: The breeder's official website URL
    #: :type: str
    breeder_url = models.URLField(
        _("Breeder's Website URL"),
        blank=True,
        null=True
    )

    @property
    def locale_breeder_url(self) -> str | None:
        """
        Get the localized breeder URL for the breeder.

        If a translation exists for the current language, it returns the translated URL.
        Otherwise, it falls back to the default breeder URL.

        :return: The localized breeder URL or the default URL.
        :rtype: str | None
        """
        translation = None
        if self.translations:
            try:
                translation = self.translations.get(language_code=get_language())
            except BreederTranslation.DoesNotExist:
                pass
            if not translation:
                try:
                    translation = self.translations.get(language_code=get_language().split('-')[0])
                except BreederTranslation.DoesNotExist:
                    pass
        if translation and translation.breeder_url:
            return translation.breeder_url
        return self.breeder_url

    #: The user who created/owns the breeder entry
    #: :type: ForeignKey
    created_by = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='breeders',
        verbose_name=_("owner"),
    )

    #: The name of the creator
    #: :type: str
    creator_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    #: The user who is the moderator of the breeder
    #:
    #: A moderator can edit the breeder details and approve strain additions
    #: If not set the creator is the moderator by default
    #: :type: ForeignKey
    moderator = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name=_("breeder moderator"),
        null=True,
        blank=True,
    )

    #: The date and time when the breeder was added
    #: :type: DateTimeField
    added_at = models.DateTimeField(
        _("added at"),
        auto_now_add=True
    )

    @property
    def created_at(self) -> date:
        """
        The date when the breeder was created.

        :return: The creation date.
        :rtype: date
        """
        return self.added_at

    updated_at = models.DateTimeField(
        _("updated at"),
        auto_now=True
    )

    @property
    def description_type(self) -> TextType:
        """
        The type of the description text.

        :return: The description text type.
        :rtype: TextType
        """
        return TextType.from_string(self.description_type_data)

    @description_type.setter
    def description_type(self, text_type: TextType | str):
        """
        Sets the description text type.

        :param text_type: The description text type.
        :type text_type: TextType | str
        """
        if not isinstance(text_type, TextType):
            text_type = TextType.from_string(TextType)
        self.description_type_data = text_type.value

    @property
    def strains_sorted(self) -> models.QuerySet:
        """
        Returns the strains of the breeder sorted by name.

        :return: The sorted strains.
        :rtype: QuerySet
        """
        return self.strains.all().order_by(Upper('name'))

    @property
    def strain_count(self) -> int:
        """


        :return: The number of strains.
        :rtype: int
        """
        return self.strains.count()

    @property
    def growlog_count(self) -> int:
        """
        Returns the total number of growlogs for all strains of the breeder.

        :return: The total number of growlogs.
        :rtype: int
        """
        if self.strain_count > 0:
            return sum(strain.growlog_count for strain in self.strains.all())
        return 0

    @property
    def strains_with_growlogs(self):
        """
        Returns a list of strains that have growlogs.
        """
        ret = []
        for strain in self.strains.all():
            if strain.growlog_count > 0:
                ret.append(strain)
        return ret

    @property
    def strains_with_growlogs_count(self) -> int:
        """
        Returns the number of strains that have growlogs.

        :return: The number of strains with growlogs.
        :rtype: int
        """

        ret = 0
        for strain in self.strains.all():
            if strain.growlog_count > 0:
                ret += 1
        return ret

    @property
    def has_logo(self) -> bool:
        """
        Returns whether the breeder has a logo image or URL set.

        :return: True if a logo exists, False otherwise.
        :rtype: bool
        """
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

    def get_translation(self, language_code: str) -> Union['BreederTranslation', None]:
        """
        Returns the breeder translation for the given language code.

        :param language_code: The language code.
        :type language_code: str
        :return: The breeder translation or None if not found.
        :rtype: BreederTranslation | None
        """
        try:
            return self.translations.get(language_code=language_code)
        except BreederTranslation.DoesNotExist:
            pass

        try:
            return self.translations.get(language_code=language_code.split('-')[0])
        except BreederTranslation.DoesNotExist:
            pass

        return None

    def __str__(self):
        return self.name

    class Meta:
        db_table = "grow_breeder"
        ordering = ['name']


class BreederTranslation(models.Model):
    """
    Breeder translation model
    """

    #: The breeder being translated
    breeder = models.ForeignKey(
        Breeder,
        on_delete=models.CASCADE,
        related_name="translations"
    )

    #: The language code of the translation
    language_code = models.CharField(
        _("language code"),
        max_length=16,
        choices=get_language_code_choices()
    )

    #: The name of the breeder in the translated language
    name = models.CharField(
        _("breeder name"),
        max_length=255,
        null=True,
        blank=True
    )

    #: The Seedfinder URL of the breeder in the translated language
    seedfinder_url = models.URLField(
        _("seedfinder url"),
        null=True,
        blank=True
    )

    #: The breeder's official website URL in the translated language
    breeder_url = models.URLField(
        _("breeder url"),
        null=True,
        blank=True
    )

    #: The description type of the translation
    description_type_data = models.CharField(
        _("description type"),
        max_length=50,
        default=TextType.MARKDOWN.value,
        choices=TEXT_CHOICES,
        db_column="description_type"
    )

    @property
    def description_type(self) -> TextType:
        """
        The type of the description text.

        :return: The description text type.
        :rtype: TextType
        """
        return TextType.from_string(self.description_type_data)

    @description_type.setter
    def description_type(self, text_type: TextType | str):
        """
        Sets the description text type.

        :param text_type: The description text type.
        :type text_type: TextType | str
        """
        if not isinstance(text_type, TextType):
            text_type = TextType.from_string(text_type)
        self.description_type_data = text_type.value

    #: The description of the strain in the translated language
    #: :type: str
    description = models.TextField(
        _("Description"),
        blank=True,
        null=True,
    )

    @property
    def description_html(self) -> SafeString | str:
        """
        Renders the description to HTML based on its type.

        :return: The HTML rendered description.
        :rtype: SafeString | str
        """
        if self.description_type == TextType.BBCODE:
            return render_description_bbcode(self.description)
        elif self.description_type == TextType.MARKDOWN:
            return render_description_markdown(self.description)
        elif self.description_type == TextType.PLAIN:
            return render_plaintext(self.description)
        else:
            return self.description

    user = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("translator"),
    )

    created_at = models.DateTimeField(
        _("created at"),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        _("updated at"),
        auto_now=True
    )

    uodated_by = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='updated_breeder_translations',
        verbose_name=_("updated by"),
    )

    class Meta:
        db_table = "grow_breeder_translation"
        unique_together = [
            ('language_code', 'breeder'),
        ]


class Strain(models.Model):
    #: The breeder of the strain
    #: :type: ForeignKey
    breeder = models.ForeignKey(
        Breeder,
        on_delete=models.CASCADE,
        related_name="strains",
        verbose_name=_("breeder")
    )

    #: The unique slug/key of the strain
    #:
    #: Used to identify the strain in URLs and API calls
    #:
    #: :type: str
    slug = models.SlugField(
        _("key"),
        max_length=255
    )
    #: The name of the strain
    #: Can be translated using the StrainTranslation model
    #: :type: str
    name = models.CharField(
        _("strain name"),
        max_length=255
    )

    @property
    def locale_name(self) -> str:
        """
        The localized name of the strain.

        This property checks for translations first and falls back to the default
        name if no translation is found.

        :return: The localized strain name.
        :rtype: str
        """
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
        if translation and translation.name:
            return translation.name
        return self.name

    #: The description of the strain
    #: Can be translated using the StrainTranslation model
    #: :type: str
    description = models.TextField(
        _("description"),
        blank=True,
        null=True
    )

    #: The type of the description text
    #: #: :type: str
    description_type_data = models.CharField(
        _("description type"),
        max_length=50,
        default=TextType.MARKDOWN.value,
        choices=TEXT_CHOICES,
        db_column="description_type"
    )

    @property
    def has_description(self) -> bool:
        """
        Checks if the strain has a description set.

        :return: True if the strain has a description, False otherwise.
        :rtype: bool
        """
        return bool(self.description)

    @property
    def description_html(self) -> SafeString | str:
        """
        The HTML rendered description of the strain.

        :return: The HTML rendered description.
        :rtype: SafeString | str
        """
        if self.description_type == TextType.BBCODE:
            return render_description_bbcode(self.description)
        elif self.description_type == TextType.MARKDOWN:
            return render_description_markdown(self.description)
        elif self.description_type == TextType.PLAIN:
            return render_plaintext(self.description)
        else:
            return self.description

    @property
    def locale_description_html(self) -> SafeString | str:
        """
        The HTML rendered description of the strain.

        This property checks for translations first and falls back to the default
        description if no translation is found.

        :return: The HTML rendered description.
        :rtype: SafeString | str
        """
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
        """
        The type of the description text (Markdown, BBCode, etc.).

        :return: The type of the description text.
        :rtype: TextType
        """
        return TextType.from_string(self.description_type_data)

    @description_type.setter
    def description_type(self, text_type: TextType | str):
        """
        Sets the description text type.

        :param text_type: The new description text type.
        :type text_type: TextType | str
        """
        if not isinstance(text_type, TextType):
            text_type = TextType.from_string(text_type)
        self.description_type_data = text_type.value

    #: The logo URL of the strain
    #: :type: str
    logo_url = models.URLField(
        _("logo url"),
        blank=True,
        null=True
    )

    #: The logo image of the strain
    #: :type: ImageField
    logo_image = models.ImageField(
        _("logo image"),
        upload_to='grow/strain/logos/',
        blank=True,
        null=True
    )

    #: The strain's official homepage URL
    #: :type: str
    strain_url = models.URLField(
        _("strain homepage"),
        null=True,
        blank=True
    )

    @property
    def locale_strain_url(self) -> str | None:
        """
        Get the localized strain URL for the strain.
        If a translation exists for the current language, it returns the translated URL.
        Otherwise, it falls back to the default strain URL.

        :return: _The localized strain URL or the default URL.
        :rtype: str | None
        """
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
        if translation and translation.strain_url:
            return translation.strain_url
        return self.strain_url

    seedfinder_url = models.URLField(
        _("seedfinder url"),
        null=True,
        blank=True
    )

    @property
    def locale_seedfinder_url(self) -> str | None:
        """
        Get the localized seedfinder URL for the strain.
        If a translation exists for the current language, it returns the translated URL.
        Otherwise, it falls back to the default seedfinder URL.

        :return: The localized seedfinder URL or the default URL.
        :rtype: str | None
        """
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
        if translation and translation.seedfinder_url:
            return translation.seedfinder_url
        return self.seedfinder_url

    #: Indicates if the strain is an autoflowering strain
    #: :type: bool
    is_automatic = models.BooleanField(
        _("is automatic"),
        default=False
    )

    #: Indicates if the you can get feminized seeds for the strain
    #: :type: bool
    is_feminized = models.BooleanField(
        _("is feminized"),
        default=True
    )

    #: Indicates if the you can get regular seeds for the strain
    #: :type: bool
    is_regular = models.BooleanField(
        _("is regular"),
        default=False
    )

    #: The flowering time of the strain in days
    #: :type: int
    flowering_time_days = models.IntegerField(
        _("flowering time (days)"),
        default=0
    )

    #: The genotype of the strain
    #: :type: str
    genotype_data = models.CharField(
        _("genotype"),
        max_length=127,
        choices=STRAIN_TYPE_CHOICES,
        default=StrainType.UNKNOWN.value,
        db_column="genotype",
    )

    #: The user who created/owns the strain entry
    #: :type: ForeignKey
    created_by = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="strains",
        verbose_name=_("created by")
    )

    #: The name of the creator
    #: :type: str
    creator_name = models.CharField(
        _("The name of the creator"),
        max_length=255,
        null=True,
        blank=True
    )

    #: The date and time when the strain was added
    #: :type: DateTimeField
    added_at = models.DateTimeField(
        _("added at"),
        auto_now_add=True,
    )

    #: Indicates if the strain is discontinued
    #: :type: bool
    is_discontinued = models.BooleanField(
        _("is discontinued"),
        default=False
    )

    @property
    def genotype(self) -> StrainType:
        """
        Get the genotype of the strain.

        :return: The genotype of the strain.
        :rtype: StrainType
        """
        return StrainType.from_string(self.genotype_data)

    @genotype.setter
    def genotype(self, genotype: StrainType | str):
        """
        Set the genotype of the strain.

        :param genetics: The genotype to set.
        :type genetics: StrainType | str
        """
        if not isinstance(genotype, StrainType):
            genotype = StrainType.from_string(genotype)

        self.genotype_data = genotype.value

    @property
    def growlog_count(self) -> int:
        """
        Get the number of growlogs for the strain.

        :return: The number of growlogs.
        :rtype: int
        """
        return self.growlog_strains.count()

    @property
    def flowering_time_weeks(self) -> int:
        """
        Get the flowering time of the strain in weeks.

        :return: The flowering time in weeks.
        :rtype: int
        """
        if not self.flowering_time_days:
            return 0

        ret = self.flowering_time_days // 7
        if (self.flowering_time_days % 7) > 3:
            ret += 1
        return ret

    @property
    def has_logo(self) -> bool:
        """
        Check if the strain has a logo image or URL set.

        :return: True if a logo exists, False otherwise.
        :rtype: bool
        """
        return (bool(self.logo_image) or bool(self.logo_url))

    @property
    def logo(self) -> str:
        """
        Get the logo image URL of the strain.

        Checks if a logo image is set; if not, it falls back to the logo URL.
        If neither is set, it returns an empty string.

        :return: The URL of the logo image.
        :rtype: str
        """
        if self.logo_image:
            return self.logo_image.url
        elif self.logo_url:
            return self.logo_url
        return ""

    def get_regular_seeds_in_stock(self, user) -> int:
        """
        Get the number of regular seeds in stock for the given user.

        :param user: The user for whom to get the seed count.
        :type user: User
        :return: The number of regular seeds in stock.
        :rtype: int
        """
        try:
            return self.seeds_in_stock.get(user=user, is_regular=True).quantity
        except StrainsInStock.DoesNotExist:
            return 0

    def get_feminized_seeds_in_stock(self, user) -> int:
        """
        Get the number of feminized seeds in stock for the given user.

        :param user: The user for whom to get the seed count.
        :type user: User
        :return: The number of feminized seeds in stock.
        :rtype: int
        """
        try:
            return self.seeds_in_stock.get(user=user, is_feminized=True).quantity
        except StrainsInStock.DoesNotExist:
            return 0

    def get_total_seeds_in_stock(self, user) -> int:
        """
        Get the total number of seeds (feminized + regular) in stock for the given user.

        :param user: The user for whom to get the seed count.
        :type user: User
        :return: The total number of seeds in stock.
        :rtype: int
        """
        return (self.get_feminized_seeds_in_stock(user)
                + self.get_regular_seeds_in_stock(user))

    def add_feminized_seeds_to_stock(self,
                                     user,
                                     quantity: int,
                                     purchased_on: date | None = None,
                                     notes: str = "",
                                     notes_type: TextType = TextType.MARKDOWN) -> int:
        """
        Adds feminized seeds to the stock for the given user.

        :param user: The user for whom to add the seeds.
        :type user: User
        :param quantity: The number of seeds to add.
        :type quantity: int
        :param purchased_on: The date the seeds were purchased, defaults to None
        :type purchased_on: date | None, optional
        :param notes: Additional notes about the seeds, defaults to ""
        :type notes: str, optional
        :param notes_type: The format of the notes, defaults to TextType.MARKDOWN
        :type notes_type: TextType, optional
        :return: The updated quantity of feminized seeds in stock.
        :rtype: int
        """

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
        """
        Removes feminized seeds from the stock for the given user.

        If the quantity to remove exceeds the current stock, it sets the stock to zero.

        If the stock reaches zero, the purchased_on date is cleared.

        :param user: The user for whom to remove the seeds.
        :type user: User
        :param quantity: The number of seeds to remove.
        :type quantity: int
        :return: The updated quantity of feminized seeds in stock.
        :rtype: int
        """
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
        """
        Adds regular seeds to the stock for the given user.

        :param user: The user for whom to add the seeds.
        :type user: User
        :param quantity: The number of seeds to add.
        :type quantity: int
        :param purchased_on: The date the seeds were purchased, defaults to None
        :type purchased_on: date | None, optional
        :param notes: Additional notes about the seeds, defaults to ""
        :type notes: str, optional
        :param notes_type: The format of the notes, defaults to TextType.MARKDOWN
        :type notes_type: TextType, optional
        :return: The updated quantity of regular seeds in stock.
        :rtype: int
        """

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
        """
        Removes regular seeds from the stock for the given user.

        If the quantity to remove exceeds the current stock, it sets the stock to zero.

        If the stock reaches zero, the purchased_on date is cleared.

        :param user: The user for whom to remove the seeds.
        :type user: User
        :param quantity: The number of seeds to remove.
        :type quantity: int
        :return: The updated quantity of regular seeds in stock.
        :rtype: int
        """
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
        """
        Gets the purchase date of feminized seeds for the given user.

        :param user: The user for whom to get the purchase date.
        :type user: User
        :return: The purchase date of feminized seeds or None if not available.
        :rtype: date | None
        """
        try:
            sis = self.seeds_in_stock.get(user=user, is_feminized=True)
            if sis.quantity > 0:
                return sis.purchased_on
            return None
        except StrainsInStock.DoesNotExist:
            return None

    def get_regular_seeds_purchased_on(self, user):
        """
        Gets the purchase date of regular seeds for the given user.

        :param user: The user for whom to get the purchase date.
        :type user: User
        :return: The purchase date of regular seeds or None if not available.
        :rtype: date | None
        """
        try:
            sis = self.seeds_in_stock.get(user=user, is_regular=True)
            if sis.quantity > 0:
                return sis.purchased_on
            return None
        except StrainsInStock.DoesNotExist:
            return None

    def get_translation(self, language_code: str) -> Union['StrainTranslation', None]:
        """
        Get the strain translation for the specified language code.

        :param language_code: The language code for the desired translation.
        :type language_code: str
        :return: The StrainTranslation object if found, otherwise None.
        :rtype: StrainTranslation | None
        """
        if language_code == "":
            return None

        try:
            return self.translations.get(language_code=language_code)
        except StrainTranslation.DoesNotExist:
            pass

        try:
            return self.translations.get(language_code=language_code.split('-')[0])
        except StrainTranslation.DoesNotExist:
            pass

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
    #: The strain being translated
    #: :type: Strain
    strain = models.ForeignKey(
        Strain,
        on_delete=models.CASCADE,
        verbose_name=_("strain"),
        related_name="translations"
    )

    #: The language code of the translation
    #: :type: str
    language_code = models.CharField(
        _("Language code"),
        max_length=16,
        choices=get_language_code_choices()
    )

    #: The name of the strain in the translated language
    #: :type: str
    name = models.CharField(
        _("strain name"),
        max_length=255,
        null=True,
        blank=True
    )

    #: The strain's official homepage URL in the translated language
    #: :type: str
    strain_url = models.URLField(
        _("strain homepage"),
        null=True,
        blank=True
    )

    #: The Seedfinder URL of the strain in the translated language
    #: :type: str
    seedfinder_url = models.URLField(
        _("seedfinder url"),
        null=True,
        blank=True
    )

    #: The description type of the translation
    #: :type: str
    description_type_data = models.CharField(
        _("description type"),
        max_length=50,
        default=TextType.MARKDOWN.value,
        choices=TEXT_CHOICES,
        db_column="description_type"
    )

    @property
    def description_type(self) -> TextType:
        """
        The type of the description text in the translated language.

        :return: The description text type.
        :rtype: TextType
        """
        return TextType.from_string(self.description_type_data)

    @description_type.setter
    def description_type(self, text_type: TextType | str):
        """
        The type of the description text in the translated language.

        :param text_type: The description text type.
        :type text_type: TextType | str
        """
        if not isinstance(text_type, TextType):
            text_type = TextType.from_string(text_type)
        self.description_type_data = text_type.value

    #: The description of the strain in the translated language
    #: :type: str
    description = models.TextField(
        _("description"),
        blank=True,
        null=True
    )

    @property
    def description_html(self) -> SafeString | str:
        """
        Renders the description to HTML based on its type.

        :return: The HTML rendered description.
        :rtype: SafeString | str
        """
        if self.description:
            if self.description_type == TextType.BBCODE:
                return render_description_bbcode(self.description)
            elif self.description_type == TextType.MARKDOWN:
                return render_description_markdown(self.description)
            elif self.description_type == TextType.PLAIN:
                return render_plaintext(self.description)
            else:
                return self.description
        return ""

    user = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("translator"),
    )

    created_at = models.DateTimeField(
        _("created at"),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        _("updated at"),
        auto_now=True,
    )

    updated_by = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="updated_strain_translations",
        verbose_name=_("updated by"),
    )

    class Meta:
        db_table = "grow_strain_translation"
        unique_together = [
            ('language_code', 'strain')
        ]


class StrainUserComment(models.Model):
    """
    User comments for strains
    """

    #: The strain being commented on
    #:
    #: type: Strain
    strain = models.ForeignKey(
        Strain,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("strain")
    )

    #: The language code of the comment
    #:
    #: type: str
    language_code = models.CharField(
        _("language"),
        max_length=16,
        choices=get_language_code_choices(),
        default=get_language(),
    )

    #: The user who made the comment
    #:
    #: type: ForeignKey
    user = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='strain_comments',
        verbose_name=_("user"),
    )

    #: The comment text
    #: type: str
    comment = models.TextField(
        _("comment")
    )

    @property
    def comment_html(self) -> SafeString | str:
        """
        Renders the comment to HTML based on its type.

        :return: The HTML rendered comment.
        :rtype: SafeString | str
        """
        if self.comment_type == TextType.BBCODE:
            return render_description_bbcode(self.comment)
        elif self.comment_type == TextType.MARKDOWN:
            return render_description_markdown(self.comment)
        elif self.comment_type == TextType.PLAIN:
            return render_plaintext(self.comment)
        else:
            return self.comment

    #: The type of the comment text
    #: type: str
    comment_type_data = models.CharField(
        _("description type"),
        max_length=50,
        default=TextType.MARKDOWN.value,
        choices=TEXT_CHOICES,
        db_column="comment_type"
    )

    @property
    def comment_type(self) -> TextType:
        """
        :description: The type of the comment text.

        :return: The comment text type.
        :rtype: TextType
        """
        return TextType.from_string(self.comment_type_data)

    @comment_type.setter
    def comment_type(self, text_type: TextType | str):
        """
        Sets the comment text type.

        :param text_type: The comment text type.
        :type text_type: TextType | str
        """
        if not isinstance(text_type, TextType):
            text_type = TextType.from_string(text_type)
        self.comment_type_data = text_type.value

    #: The date and time when the comment was created
    created_at = models.DateTimeField(
        _("created at"),
        auto_now_add=True
    )

    #: The date and time when the comment was last updated
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
    """
    User uploaded strain images
    """

    #: The strain the image is associated with
    #:
    #: type: Strain
    strain = models.ForeignKey(
        Strain,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("user description"),
    )
    #: The user who uploaded the image
    #:
    #: type: ForeignKey
    uploader = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        related_name="strain_images",
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        editable=False,
    )

    #: The uploaded image file
    #: type: ImageField
    image = models.ImageField(
        _("image"),
        upload_to='grow/strain/user_images/'
    )

    #: The date and time when the image was uploaded
    #: type: DateTimeField
    uploaded_at = models.DateTimeField(
        _("uploaded at"),
        auto_now_add=True
    )

    #: The name of the uploader
    #: type: str
    uploader_name = models.CharField(
        _("uploader"),
        max_length=255,
        null=True,
        blank=True,
        db_column="uploader_name"
    )

    #: The description of the image
    #: type: str
    description = models.TextField(
        _("description"),
        null=True,
        blank=True
    )

    #: The type of the description text
    #: type: str
    description_type_data = models.CharField(
        _("description"),
        max_length=50,
        default=TextType.MARKDOWN.value,
        choices=TEXT_CHOICES
    )

    #: The caption of the image
    #: type: str
    caption = models.CharField(
        _("caption"),
        max_length=255,
        null=True,
        blank=True
    )

    @property
    def description_type(self) -> TextType:
        """
        The type of the description text.

        :return: The description text type.
        :rtype: TextType
        """
        return TextType.from_string(self.description_type_data)

    @description_type.setter
    def description_type(self, text_type: TextType | str):
        """
        Sets the description text type.

        :param text_type: The description text type.
        :type text_type: TextType | str
        """
        if not isinstance(text_type, TextType):
            text_type = TextType.from_string(text_type)
        self.description_type_data = text_type.value

    class Meta:
        db_table = "grow_strain_image"


class StrainsInStock(models.Model):
    """
    Tracks seeds in stock for strains per user.
    """

    #: The strain the seeds in stock belong to
    #: type: ForeignKey
    strain = models.ForeignKey(Strain,
                               on_delete=models.CASCADE,
                               related_name="seeds_in_stock",
                               verbose_name=_("strain"))

    #: The user who owns the seeds in stock
    #: type: ForeignKey
    user = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='seeds_in_stock',
        verbose_name=_("user"),
    )

    #: Whether the seeds are regular
    #: type: bool
    is_regular = models.BooleanField(
        _("regular seeds"),
        default=False
    )

    #: Whether the seeds are feminized
    #: type: bool
    is_feminized = models.BooleanField(
        _("feminized seeds"),
        default=True
    )

    #: The quantity of seeds in stock
    #: type: int
    quantity = models.IntegerField(
        _("quantity"),
        default=0
    )

    #: The last date when the seeds were purchased
    #: type: date
    purchased_on = models.DateField(
        _("purchased on"),
        blank=True,
        null=True
    )

    #: Additional notes about the seeds
    #: type: str
    notes = models.TextField(
        _("notes"),
        blank=True,
        null=True
    )

    @property
    def notes_html(self) -> SafeString | str:
        """
        Renders the notes to HTML based on its type.

        :return: The HTML rendered notes.
        :rtype: SafeString | str
        """
        if self.notes:
            if self.notes_type == TextType.BBCODE:
                return render_description_bbcode(self.notes)
            elif self.notes_type == TextType.MARKDOWN:
                return render_description_markdown(self.notes)
            elif self.notes_type == TextType.PLAIN:
                return render_plaintext(self.notes)
            else:
                return self.notes
        return ""

    #: The type of the notes text
    #: type: str
    notes_type_data = models.CharField(
        _("text type"),
        max_length=50,
        choices=TEXT_CHOICES,
        default=TextType.MARKDOWN.value,
        db_column="notes_type",
    )

    @property
    def notes_type(self) -> TextType:
        """
        The type of the notes text.

        :return: The notes text type.
        :rtype: TextType
        """
        return TextType.from_string(self.notes_type_data)

    @notes_type.setter
    def notes_type(self, text_type: TextType | str):
        """
        Sets the notes text type.
        :param text_type: The notes text type.
        :type text_type: TextType | str
        """
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
