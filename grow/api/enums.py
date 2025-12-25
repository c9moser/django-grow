"""
Enums and constantcs for the GrowControl API.
"""
from enum import StrEnum
from django.utils.translation import (
    gettext_noop as _,
    gettext_lazy,
    gettext
)


class LocationType(StrEnum):
    """
    Grow location enumeration.
    """

    #: Indoor grow location
    INDOOR = "indoor"

    #: Outdoor grow location
    OUTDOOR = "outdoor"

    #: Greenhouse grow location
    GREENHOUSE = "greenhouse"

    #: Balcony grow location
    BALCONY = "balcony"

    @staticmethod
    def from_string(location_str: str) -> 'LocationType':
        mapping = {
            "indoor": LocationType.INDOOR,
            "outdoor": LocationType.OUTDOOR,
            "greenhouse": LocationType.GREENHOUSE,
            "balcony": LocationType.BALCONY,
        }
        try:
            return mapping.get(location_str.lower())
        except KeyError:
            raise ValueError(f"Unknown location: {location_str}")

    @property
    def name_raw(self) -> str:
        mapping = {
            LocationType.INDOOR: "indoor",
            LocationType.OUTDOOR: "outdoor",
            LocationType.GREENHOUSE: "greenhouse",
            LocationType.BALCONY: "balcony",
        }
        return mapping[self]

    @property
    def name_lazy(self) -> str:
        return gettext_lazy(self.name_raw)

    @property
    def name(self) -> str:
        return gettext(self.name_raw)

    def __str__(self) -> str:
        return self.value

    def __repr__(self):
        return f"<GrowLocation: {self.value.upper()}>"


LOCATION_TYPES = [
    GrowLocationType.INDOOR,
    GrowLocationType.OUTDOOR,
    GrowLocationType.GREENHOUSE,
    GrowLocationType.BALCONY,
]


class GrowLightType(StrEnum):
    """
    Grow light type enumeration.
    """

    #: LED grow light
    LED = "led"

    #: HPS grow light
    HPS = "hps"

    #: HPS grow light
    HIGH_PRESSURE_SODIUM = "hps"

    #: Fluorescent grow light
    FLUORESCENT = "fluorescent"

    #: Metal Halide grow light
    MH = "mh"
    #: Metal Halide grow light
    METAL_HALIDE = "mh"

    @staticmethod
    def from_string(light_str: str) -> 'GrowLightType':
        mapping = {
            "led": GrowLightType.LED,
            "hps": GrowLightType.HPS,
            "high_pressure_sodium": GrowLightType.HPS,
            "mh": GrowLightType.MH,
            "metal_halide": GrowLightType.MH,
            "fluorescent": GrowLightType.FLUORESCENT,
        }
        try:
            return mapping.get(light_str.lower())
        except KeyError:
            raise ValueError(f"Unknown light type: {light_str}")

    @property
    def name_raw(self) -> str:
        mapping = {
            GrowLightType.LED: "led",
            GrowLightType.HPS: _("High Pressure Sodium"),
            GrowLightType.HIGH_PRESSURE_SODIUM: _("High Pressure Sodium"),
            GrowLightType.MH: _("Metal Halide"),
            GrowLightType.METAL_HALIDE: _("Metal Halide"),
            GrowLightType.FLUORESCENT: "fluorescent",
        }
        return mapping[self]

    @property
    def name_lazy(self) -> str:
        return gettext_lazy(self.name_raw)

    @property
    def name(self) -> str:
        return gettext(self.name_raw)

    def __str__(self) -> str:
        return self.value

    def __repr__(self):
        return f"<GrowLightType: {self.value.upper()}>"


GROW_LIGHT_TYPES = [
    GrowLightType.LED,
    GrowLightType.HPS,
    GrowLightType.MH,
    GrowLightType.FLUORESCENT,
]


class GrowMediumType(StrEnum):
    """
    Grow medium type enumeration.
    """

    #: Soil grow medium
    SOIL = "soil"

    #: Hydroponic grow medium
    HYDROPONIC = "hydroponic"

    #: Aeroponic grow medium
    AEROPONIC = "aeroponic"

    @staticmethod
    def from_string(medium_str: str) -> 'GrowMediumType':
        mapping = {
            "soil": GrowMediumType.SOIL,
            "hydroponic": GrowMediumType.HYDROPONIC,
            "aeroponic": GrowMediumType.AEROPONIC,
        }
        try:
            return mapping.get(medium_str.lower())
        except KeyError:
            raise ValueError(f"Unknown grow medium: {medium_str}")

    @property
    def name_raw(self) -> str:
        mapping = {
            GrowMediumType.SOIL: "soil",
            GrowMediumType.HYDROPONIC: "hydroponic",
            GrowMediumType.AEROPONIC: "aeroponic",
        }
        return mapping[self]

    @property
    def name_lazy(self) -> str:
        return gettext_lazy(self.name_raw)

    @property
    def name(self) -> str:
        return gettext(self.name_raw)

    def __str__(self) -> str:
        return self.value

    def __repr__(self):
        return f"<GrowMediumType: {self.value.upper()}>"


GROW_MEDIUM_TYPES = [
    GrowMediumType.SOIL,
    GrowMediumType.HYDROPONIC,
    GrowMediumType.AEROPONIC,
]


class TextType(StrEnum):
    """
    Text type enumeration.
    """

    PLAIN = "plain"
    MARKDOWN = "markdown"
    BBCODE = "bbcode"
    HTML = "html"

    @staticmethod
    def from_string(text_str: str) -> 'TextType':
        mapping = {
            "plain": TextType.PLAIN,
            "bbcode": TextType.BBCODE,
            "markdown": TextType.MARKDOWN,
            "html": TextType.HTML,
        }
        try:
            return mapping.get(text_str.lower())
        except KeyError:
            raise ValueError(f"Unknown text type: {text_str}")

    @property
    def name_raw(self) -> str:
        mapping = {
            TextType.PLAIN: "plain",
            TextType.MARKDOWN: "markdown",
            TextType.HTML: "html",
            TextType.BBCODE: "bbcode",
        }
        return mapping[self]

    @property
    def name_lazy(self) -> str:
        return gettext_lazy(self.name_raw)

    @property
    def name(self) -> str:
        return gettext(self.name_raw)

    def __str__(self) -> str:
        return self.value

    def __repr__(self):
        return f"<TextType: {self.value.upper()}>"


TEXT_TYPES = [
    TextType.PLAIN,
    TextType.MARKDOWN,
    TextType.BBCODE,
    TextType.HTML,
]


class StrainType(StrEnum):
    """
    Strain type enumeration.
    """

    INDICA = "indica"
    INDICA_RUDERALIS = "indica_ruderalis"
    SATIVA = "sativa"
    SATIVA_RUDERALIS = "sativa_ruderalis"
    MOSTLY_INDICA = "mostly_indica"
    MOSTLY_SATIVA = "mostly_sativa"
    HYBRID = "hybrid"
    HYBRID_RUDERALIS = "hybrid_ruderalis"
    RUDERAILIS = "ruderalis"

    @staticmethod
    def from_string(strain_str: str) -> 'StrainType':
        mapping = {
            "indica": StrainType.INDICA,
            "sativa": StrainType.SATIVA,
            "hybrid": StrainType.HYBRID,
            "indica_ruderalis": StrainType.INDICA_RUDERALIS,
            "sativa_ruderalis": StrainType.SATIVA_RUDERALIS,
            "hybrid_ruderalis": StrainType.HYBRID_RUDERALIS,
            "mostly_indica": StrainType.MOSTLY_INDICA,
            "mostly_sativa": StrainType.MOSTLY_SATIVA,
            "ruderalis": StrainType.RUDERAILIS,
        }
        try:
            return mapping.get(strain_str.lower())
        except KeyError:
            raise ValueError(f"Unknown strain type: {strain_str}")

    @property
    def name_raw(self) -> str:
        mapping = {
            StrainType.INDICA: "indica",
            StrainType.SATIVA: "sativa",
            StrainType.HYBRID: "indica/sativa hybrid",
            StrainType.INDICA_RUDERALIS: "indica/ruderalis hybrid",
            StrainType.SATIVA_RUDERALIS: "sativa/ruderalis hybrid",
            StrainType.HYBRID_RUDERALIS: "indica/sativa/ruderalis hybrid",
            StrainType.MOSTLY_INDICA: "mostly indica",
            StrainType.MOSTLY_SATIVA: "mostly sativa",
            StrainType.RUDERAILIS: "ruderalis",
        }
        return mapping[self]

    @property
    def name_lazy(self) -> str:
        return gettext_lazy(self.name_raw)

    @property
    def name(self) -> str:
        return gettext(self.name_raw)

    def __str__(self) -> str:
        return self.value

    def __repr__(self):
        return f"<StrainType: {self.value.upper()}>"


STRAIN_TYPES = [
    StrainType.INDICA,
    StrainType.SATIVA,
    StrainType.RUDERAILIS,
    StrainType.INDICA_RUDERALIS,
    StrainType.SATIVA_RUDERALIS,
    StrainType.MOSTLY_INDICA,
    StrainType.MOSTLY_SATIVA,
    StrainType.HYBRID,
    StrainType.HYBRID_RUDERALIS,
]


class GrowPermissionType(StrEnum):
    """
    Growlog permission type enumeration.
    """

    PUBLIC = "public"
    PRIVATE = "private"
    MEMBERS_ONLY = "members_only"
    FRIENDS = "friends_only"

    @staticmethod
    def from_string(permission_str: str) -> 'GrowPermissionType':
        mapping = {
            "public": GrowPermissionType.PUBLIC,
            "private": GrowPermissionType.PRIVATE,
            "members_only": GrowPermissionType.MEMBERS_ONLY,
            "friends_only": GrowPermissionType.FRIENDS,
        }
        try:
            return mapping.get(permission_str.lower())
        except KeyError:
            raise ValueError(f"Unknown permission type: {permission_str}")

    @property
    def name_raw(self) -> str:
        mapping = {
            GrowPermissionType.PUBLIC: "public",
            GrowPermissionType.PRIVATE: "private",
            GrowPermissionType.MEMBERS_ONLY: "members only",
            GrowPermissionType.FRIENDS: "friends only",
        }
        return mapping[self]

    @property
    def name_lazy(self) -> str:
        return gettext_lazy(self.name_raw)

    @property
    def name(self) -> str:
        return gettext(self.name_raw)

    def __str__(self) -> str:
        return self.value

    def __repr__(self):
        return f"<GrowlogPermissionType: {self.value.upper()}>"


GROW_PERMISSION_TYPES = [
    GrowPermissionType.FRIENDS,
    GrowPermissionType.MEMBERS_ONLY,
    GrowPermissionType.PRIVATE,
    GrowPermissionType.PUBLIC,
]


class SensorType(StrEnum):
    """
    Sensor type enumeration.
    """

    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    PH = "ph"
    EC = "ec"
    SOIL_MOISTURE = "soil_moisture"
    LIGHT_INTENSITY = "light_intensity"
    CO2_LEVEL = "co2_level"
    TEMPERATURE_MEDIUM = "temperature_medium"

    @staticmethod
    def from_string(sensor_str: str) -> 'SensorType':
        mapping = {
            "temperature": SensorType.TEMPERATURE,
            "humidity": SensorType.HUMIDITY,
            "soil_moisture": SensorType.SOIL_MOISTURE,
            "light_intensity": SensorType.LIGHT_INTENSITY,
            "co2_level": SensorType.CO2_LEVEL,
        }
        try:
            return mapping.get(sensor_str.lower())
        except KeyError:
            raise ValueError(f"Unknown sensor type: {sensor_str}")

    @property
    def name_raw(self) -> str:
        mapping = {
            SensorType.TEMPERATURE: "temperature",
            SensorType.HUMIDITY: "humidity",
            SensorType.SOIL_MOISTURE: "soil moisture",
            SensorType.LIGHT_INTENSITY: "light intensity",
            SensorType.CO2_LEVEL: "CO2 level",
            SensorType.PH: "pH",
            SensorType.EC: "electrical conductivity",
            SensorType.TEMPERATURE_MEDIUM: "medium temperature",
        }
        return mapping[self]

    @property
    def name_lazy(self) -> str:
        return gettext_lazy(self.name_raw)

    @property
    def name(self) -> str:
        return gettext(self.name_raw)

    def __str__(self) -> str:
        return self.value

    def __repr__(self):
        return f"<SensorType: {self.value.upper()}>"
