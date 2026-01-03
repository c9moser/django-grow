"""
Location models
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

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
        editable=False
    )

    #: The description of the location
    description = models.TextField(
        _("description"),
        blank=True,
        null=True
    )

    #: The TextType of the description
    description_type = models.CharField(
        _("description type"),
        max_length=50,
        default=TextType.MARKDOWN.value,
        choices=TEXT_CHOICES
    )

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
        return LocationType(self.location_type_data)

    @location_type.setter
    def location_type(self, value: LocationType):
        self.location_type_data = value.value

    @property
    def permission(self):
        return PermissionType.from_string(self.permission_data)

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

    #: The light cycle in hours
    light_cycle_hours = models.PositiveIntegerField(
        _("light cycle hours"),
        help_text=_("Number of hours the light is on during a 24-hour period."),
        default=12
    )

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
    ventilation_intesity = models.PositiveIntegerField(
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
        related_name="outdoor_locations",
        verbose_name=_("location")
    )

    #: the longitude of the location
    logitude = models.DecimalField(
        _("longitude"),
        max_digits=9,
        decimal_places=6,
    )

    #: The latitude of the location
    latitude = models.DecimalField(
        _("latitude"),
        max_digits=10,
        decimal_places=3,
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
