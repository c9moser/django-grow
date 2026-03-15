"""
Location models
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils.safestring import mark_safe

from ..enums import (
    LocationType,
    LOCATION_CHOICES,
    GrowLightType,
    GROW_LIGHT_CHOICES,
    TextType,
    TEXT_CHOICES,
    PermissionType,
    PERMISSION_CHOICES,
)


class Location(models.Model):
    #: The key(slug) of the location
    key = models.SlugField(
        _("key"),
        max_length=255,
        null=False,
        blank=False,
    )

    #: The location name
    name = models.CharField(
        _("name"),
        max_length=255,
        unique=True
    )

    #: The location type (indoor, outdoor, ...)
    location_type_data = models.CharField(
        _("location type"),
        max_length=50,
        choices=LOCATION_CHOICES,
        default=LocationType.INDOOR.value,
    )

    #: The description of the location
    description = models.TextField(
        _("description"),
        blank=True,
        null=True
    )

    @property
    def description_html(self) -> str:
        """
        Returns the HTML representation of the description.
        """
        if self.description:
            if self.description_type == TextType.MARKDOWN:
                from grow.growapi.parser.markdown import render_description_markdown
                return render_description_markdown(self.description)
            elif self.description_type == TextType.BBCODE:
                from grow.growapi.parser.bbcode import render_description_bbcode
                return render_description_bbcode(self.description)
            elif self.description_type == TextType.PLAIN:
                return mark_safe(self.description.replace("\n", "<br>"))
        else:
            return ""

    #: The TextType of the description
    description_type_data = models.CharField(
        _("description type"),
        max_length=50,
        default=TextType.MARKDOWN.value,
        choices=TEXT_CHOICES,
        db_column='description_type'
    )

    @property
    def description_type(self) -> TextType:
        """
        Get/Set the :py:class:`TextType` of the description.
        """
        return TextType.from_string(self.description_type_data)

    @description_type.setter
    def description_type(self, texttype: TextType | str):
        if isinstance(texttype, str):
            texttype = TextType.from_string(texttype)
        elif not isinstance(texttype, TextType):
            raise ValueError("description_type must be a TextType or str")
        self.description_type_data = texttype.value()

    #: The visibility of the location
    #:
    #: **Note**: Use the `permission` property to get/set permissions.
    permission_data = models.CharField(
        _("Permission"),
        help_text=_("This defines who can view the location details. If not permitted to view details only the location type is shown."),  # noqa: E501
        max_length=50,
        default=PermissionType.MEMBERS_ONLY.value,
        choices=PERMISSION_CHOICES,
        db_column='permission'
    )

    #: The owner of the location
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='locations',
        verbose_name=_("owner"),
    )

    @property
    def location_type(self):
        """
        Sets the visibility of the location.

        If the the user is not permitted to view the location,
        only the location type is shown.
        """
        return LocationType.from_string(self.location_type_data)

    @location_type.setter
    def location_type(self, value: LocationType):
        self.location_type_data = value.value

    @property
    def permission(self):
        return PermissionType.from_string(self.permission_data)

    @property
    def growlogs(self):
        growlogs = set()
        for entry in self.growlog_entries.all():
            growlogs.add(entry.growlog)
        return growlogs

    def __str__(self):
        return self.name

    class Meta:
        db_table = "grow_location"
        unique_together = [
            ('owner', 'key'),
        ]


class GrowRoom(models.Model):
    """
    The growroom for indoor grows.
    """

    #: The location for the growroom
    location = models.OneToOneField(
        Location,
        on_delete=models.CASCADE,
        related_name="grow_room",
        verbose_name=_("location")
    )

    #: The light type of the growroom
    #:
    #: **Note:** Use the `light_type` property to get/set the light type.
    light_type_data = models.CharField(
        _("lighting"),
        max_length=255,
        choices=GROW_LIGHT_CHOICES,
        default=GrowLightType.LED.value,
    )

    @property
    def light_type(self) -> GrowLightType:
        """
        Get/Set the :py:class:`GrowLightType` of the growroom.
        """
        return GrowLightType.from_string(self.light_type_data)

    @light_type.setter
    def light_type(self, lighttype: GrowLightType | str):
        if isinstance(lighttype, str):
            lighttype = GrowLightType.from_string(lighttype)
        elif not isinstance(lighttype, GrowLightType):
            raise ValueError("light_type must be a GrowLightType or str")
        self.light_type_data = lighttype.value

    #: The maximum light intensity in lumens
    light_intensity = models.PositiveIntegerField(
        _("light intensity"),
        help_text=_("Light intensity in lumens."),
        default=0
    )

    #: The maximum power consuption in Watts
    light_power_consumption = models.PositiveIntegerField(
        _("light power consumption"),
        help_text=_("Power consumption in Watts."),
        default=0
    )

    #: The maximum ventilation intensity
    ventilation_intensity = models.PositiveIntegerField(
        _("ventilation intensity"),
        help_text=_("Ventilation intensity in cubic meters per hour."),
        default=0
    )

    #: The maximum ventilation power consumption
    ventilation_power_consumption = models.PositiveIntegerField(
        _("ventilation power consumption"),
        help_text=_("Power consumption in Watts."),
        default=0
    )

    # The width of the growroom
    width = models.PositiveIntegerField(
        _("width"),
        default=120,
        help_text=_("Width in centimeters.")
    )

    # The height of the growroom
    height = models.PositiveIntegerField(
        _("height"),
        default=120,
        help_text=_("Height in centimeters.")
    )

    # The depth of the growroom
    depth = models.PositiveIntegerField(
        _("depth"),
        default=200,
        help_text=_("Depth in centimeters.")
    )

    @property
    def area(self):
        """
        Returns the area of the growroom in square meters.
        """
        return (self.width * self.depth) / 10000

    @property
    def volume(self):
        """
        Returns the volume of the growroom in cubic meters.
        """
        return (self.width * self.depth * self.height) / 1000000

    class Meta:
        db_table = "grow_growroom"


class OutdoorLocation(models.Model):
    """
    The Outdoor location data.

    You can set the longitude and latitude to find your plants again
    if you are growing in an uncommon location.
    """

    #: the outdoor data for the location
    location = models.OneToOneField(
        Location,
        on_delete=models.CASCADE,
        related_name="outdoor_location",
        verbose_name=_("location")
    )

    #: the longitude of the location
    longitude = models.DecimalField(
        _("longitude"),
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True
    )

    #: The latitude of the location
    latitude = models.DecimalField(
        _("latitude"),
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True
    )

    #: additional notes personal notes
    #:
    #: Only the owner of the location can view the
    #: the notes
    notes = models.TextField(
        _("description"),
        blank=True,
        null=True
    )

    #: the TextType of the notes
    notes_type_data = models.CharField(
        _("description type"),
        max_length=50,
        default="markdown",
        choices=TEXT_CHOICES
    )

    @property
    def notes_type(self) -> TextType:
        """
        Get/Set the :py:class:`TextType` of the notes.
        """
        return TextType.from_string(self.notes_type_data)

    @notes_type.setter
    def notes_type(self, texttype: TextType):
        self.notes_type_data = texttype.value()

    class Meta:
        db_table = "grow_outdoorlocation"
