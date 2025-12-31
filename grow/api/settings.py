"""
grow.api settings
"""

from django.conf import settings
from pathlib import Path
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


GROW_EXPORTS_VERSIONS = getattr(settings, "GROW_EXPRTS_VERSIONS", 3)
GROW_EXPORTS_DIR = getattr(settings, 'GROW_EXPORTS_DIR',
                           Path(settings.MEDIA_ROOT) / "grow" / "exports")

if isinstance(GROW_EXPORTS_DIR, str):
    GROW_EXPORTS_DIR = Path(GROW_EXPORTS_DIR).resolve()

GROW_EXPORTS_FILE_FORMAT = str(GROW_EXPORTS_DIR / "grow-exports-{date}.zip")
GROW_EXPORTS_VERSIONS_FILE = GROW_EXPORTS_DIR / "grow-exports.versions"

INCLUDE_WIKI = getattr(settings, "INCLUDE_WIKI", False)
USE_BOOTSTRAP = getattr(settings, "USE_BOOTSTRAP", False)
