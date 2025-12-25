"""
Location models
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import CheckConstraint, Q
from django.conf import settings

from ..enums import (
    GrowLocationType,
    GrowLightType,
    TextType,
    TEXT_TYPES,
    LOCATION_TYPES,
)


class Location(models.Model):
    key = models.SlugField(_("key"),
                           max_length=255,
                           unique=True)
    name = models.CharField(_("name"),
                            max_length=255,
                            unique=True)
    location_type_data = models.CharField(_("location type"),
                                          max_length=50,
                                          choices=[
                                              (lt.value, lt.name_lazy)
                                              for lt in LOCATION_TYPES
                                              ],
                                          editable=False)
    description = models.TextField(_("description"),
                                   blank=True,
                                   null=True)
    description_type = models.CharField(_("description type"),
                                        max_length=50,
                                        default="markdown",
                                        choices=[
                                            (tt.value, tt.name_lazy)
                                            for tt in TEXT_TYPES
                                        ])

    onwer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='locations',
        verbose_name=_("owner"),
    )

    @property
    def location_type(self):
        return GrowLocationType(self.location_type_data)

    @location_type.setter
    def location_type(self, value: GrowLocationType):
        self.location_type_data = value.value

    class Meta:
        table_name = "grow_location"


class GrowRoom(models.Model):
    key = models.SlugField(_("key"),
                           max_length=255,
                           unique=True)
    name = models.CharField(_("name"),
                            max_length=255)

    location = models.OneToOneField(Location,
                                    on_delete=models.CASCADE,
                                    related_name="grow_room",
                                    verbose_name=_("location"))

    light = models.CharField(_("lighting"),
                             max_length=255,
                             choices=[
                                 (glt.value, glt.name_lazy)
                                 for glt in GrowLightType
                        ])

    light_cycle_hours = models.PositiveIntegerField(
        _("light cycle hours"),
        help_text=_("Number of hours the light is on during a 24-hour period."),
        default=12
    )

    light_intensity = models.PositiveIntegerField(
        _("light intensity"),
        help_text=_("Light intensity in lumens."),
        default=0
    )

    light_power_consumption = models.PositiveIntegerField(
        _("light power consumption"),
        help_text=_("Power consumption in Watts."),
        default=0
    )

    ventilation_intesity = models.PositiveIntegerField(
        _("ventilation intensity"),
        help_text=_("Ventilation intensity in cubic meters per hour."),
        default=0
    )

    ventilation_power_consumption = models.PositiveIntegerField(
        _("ventilation power consumption"),
        help_text=_("Power consumption in Watts."),
        default=0
    )

    width = models.PositiveIntegerField(_("width"),
                                        default=120,
                                        help_text=_("Width in centimeters."))
    height = models.PositiveIntegerField(_("height"),
                                         default=120,
                                         help_text=_("Height in centimeters."))
    depth = models.PositiveIntegerField(_("depth"),
                                        default=200,
                                        help_text=_("Depth in centimeters."))

    description = models.TextField(_("description"),
                                   blank=True,
                                   null=True)
    description_type = models.CharField(_("description type"),
                                        max_length=50,
                                        default="markdown",
                                        choices=[
                                            (tt.value, tt.name_lazy)
                                            for tt in TextType
                                        ])

    class Meta:
        db_table = "grow_growroom"
        constraints = [
            CheckConstraint(
                Q(location__location_type=GrowLocationType.INDOOR.value),
                name="growroom_location_indoor_only"),
        ]


class OutdoorLocation(models.Model):
    key = models.SlugField(_("key"),
                           max_length=255,
                           unique=True)
    name = models.CharField(_("name"),
                            max_length=255)

    location = models.OneToOneField(Location,
                                    on_delete=models.CASCADE,
                                    related_name="outdoor_locations",
                                    verbose_name=_("location"))
    logitude = models.DecimalField(_("longitude"),
                                   max_digits=9,
                                   decimal_places=6,
                                   null=True,
                                   blank=True)
    latitude = models.DecimalField(_("latitude"),
                                   max_digits=9,
                                   decimal_places=6,
                                   null=True,
                                   blank=True)

    description = models.TextField(_("description"),
                                   blank=True,
                                   null=True)
    description_type = models.CharField(_("description type"),
                                        max_length=50,
                                        default="markdown",
                                        choices=[
                                            (tt.value, tt.name_lazy)
                                            for tt in TextType
                                        ])

    class Meta:
        db_table = "grow_outdoorlocation"
        constraints = [
            CheckConstraint(
                Q(location__location_type=GrowLocationType.OUTDOOR.value),
                name="growroom_location_outdoor_only"),
        ]
