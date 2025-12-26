"""
grow.api settings
"""

from django.conf import settings
from .enums import (
    PermissionType,
    TextType,
)

AUTH_USER_MODEL = settings.AUTH_USER_MODEL
GROW_SENSOR_READINGS_PER_DAY = getattr(settings,
                                       'GROW_SENSOR_READINGS_PER_DAY',
                                       False)

GROW_SENSOR_READINGS_PER_DAY_COMPRESSED = getattr(settings,
                                                  'GROW_SENSOR_REAIDNGS_PER_DAY_COMPRESSED',
                                                  False)
GROW_DEFAULT_PERMISSION = getattr(settings,
                                  'GROW_DEFAULT_PERMSSION',
                                  PermissionType.PRIVATE)
if isinstance(GROW_DEFAULT_PERMISSION, str):
    GROW_DEFAULT_PERMISSION = PermissionType.from_string(GROW_DEFAULT_PERMISSION)

GROW_DEFAULT_TEXT_TYPE = getattr(settings,
                                 'GROW_DEFAULT_TEXT_TYPE',
                                 TextType.MARKDOWN)

if isinstance(GROW_DEFAULT_TEXT_TYPE, str):
    GROW_DEFAULT_TEXT_TYPE = TextType.from_string(GROW_DEFAULT_TEXT_TYPE)
