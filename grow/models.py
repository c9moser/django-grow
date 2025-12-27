from django.db import models
from django.utils.translation import gettext_lazy as _

from .api.enums import (
    PermissionType,
    PERMISSION_CHOICES,
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

    location_permission_data = models.CharField(
        _("Default location permission"),
        max_length=50,
        choices=PERMISSION_CHOICES,
        default=PermissionType.PRIVATE.value
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
