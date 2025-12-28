from django.db import models
from django.utils.translation import gettext_lazy as _

from .enums import (
    PermissionType,
    PERMISSION_CHOICES,
    LengthUnit,
    LENGTH_UNIT_CHOICES,
    TemperatureUnit,
    TEMPERATURE_UNIT_CHOICES,
)


class UserSettings(models.Model):
    #: default Growlog permission
    #:
    #: This defines the default visibility for new Growlogs
    growlog_permission_data = models.CharField(
        _("Default growlog permission"),
        max_length=50,
        choices=PERMISSION_CHOICES,
        default=PermissionType.PRIVATE.value,
    )

    #: Default location permission
    #:
    #: This defines the default location permission
    location_permission_data = models.CharField(
        _("Default location permission"),
        max_length=50,
        choices=PERMISSION_CHOICES,
        default=PermissionType.PRIVATE.value
    )

    #: Units of length
    #:
    #: Sets the unit of length the user wants to display.
    #: The WebAPI returns the the metric data always.
    length_unit = models.CharField(
        _("unit of length"),
        max_length=50,
        default=LengthUnit.METRIC,
        choices=LENGTH_UNIT_CHOICES
    )

    #: Temerature units
    #:
    #: Sets the temperature unit you wants to display.
    #: The WebAPI returns the data in Celcius always.
    temperature_unit = models.CharField(
        max_length=1,
        default=TemperatureUnit.CELCIUS,
        choices=TEMPERATURE_UNIT_CHOICES
    )

    @property
    def growlog_permission(self) -> PermissionType:
        return PermissionType.from_string(self.growlog_permission_data)

    @growlog_permission.setter
    def growlog_permission(self, permission: PermissionType):
        self.growlog_permission_data = permission.value

    @property
    def location_permission(self) -> PermissionType:
        return PermissionType.from_string(self.location_permission_data)

    @location_permission.setter
    def location_permission(self, permission: PermissionType):
        self.location_permission_data = permission.from_string(permission)
