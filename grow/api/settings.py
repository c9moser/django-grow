"""
grow.api settings
"""

from django.conf import settings
from .enums import (
    PermissionType,
    TextType,
)

AUTH_USER_MODEL = settings.AUTH_USER_MODEL
GRC_SENSOR_READINGS_PER_DAY = getattr(settings,
                                      'GRC_SENSOR_READINGS_PER_DAY',
                                      False)

GRC_SENSOR_READINGS_PER_DAY_COMPRESSED = getattr(settings,
                                                 'GRC_SENSOR_REAIDNGS_PER_DAY_COMPRESSED',
                                                 False)
GRC_DEFAULT_PERMISSION = getattr(settings,
                                 'GRC_DEFAULT_PERMSSION',
                                 PermissionType.PRIVATE)
if isinstance(GRC_DEFAULT_PERMISSION, str):
    GRC_DEFAULT_PERMISSION = PermissionType.from_string(GRC_DEFAULT_PERMISSION)

GRC_DEFAULT_TEXT_TYPE = getattr(settings,
                                'GRC_DEFAULT_TEXT_TYPE',
                                TextType.MARKDOWN)

if isinstance(GRC_DEFAULT_TEXT_TYPE, str):
    GRC_DEFAULT_TEXT_TYPE = TextType.from_string(GRC_DEFAULT_TEXT_TYPE)
