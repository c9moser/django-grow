"""
Enums and constantcs for the GrowControl API.
"""
from enum import StrEnum, IntEnum
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
            LocationType.INDOOR: _("indoor"),
            LocationType.OUTDOOR: _("outdoor"),
            LocationType.GREENHOUSE: _("greenhouse"),
            LocationType.BALCONY: _("balcony"),
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
    LocationType.INDOOR,
    LocationType.OUTDOOR,
    LocationType.GREENHOUSE,
    LocationType.BALCONY,
]

LOCATION_CHOICES = [(lt.value, lt.name_lazy) for lt in LocationType]


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
            GrowLightType.LED: _("led"),
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

GROW_LIGHT_CHOICES = [(glt.value, glt.name_lazy) for glt in GROW_LIGHT_TYPES]


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
            GrowMediumType.SOIL: _("soil"),
            GrowMediumType.HYDROPONIC: _("hydroponic"),
            GrowMediumType.AEROPONIC: _("aeroponic"),
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
GROW_MEDIUM_CHOICES = [(gmt.value, gmt.name_lazy) for gmt in GROW_MEDIUM_TYPES]


class TextType(StrEnum):
    """
    Text type enumeration.
    """

    MARKDOWN = "markdown"
    BBCODE = "bbcode"
    PLAIN = "plaintext"

    @staticmethod
    def from_string(text_str: str) -> 'TextType':
        mapping = {
            "bbcode": TextType.BBCODE,
            "markdown": TextType.MARKDOWN,
            "plaintext": TextType.PLAIN
        }
        try:
            return mapping.get(text_str.lower())
        except KeyError:
            raise ValueError(f"Unknown text type: {text_str}")

    @property
    def name_raw(self) -> str:
        mapping = {
            TextType.MARKDOWN: _("markdown"),
            TextType.BBCODE: _("bbcode"),
            TextType.PLAIN: _("plain text"),
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
    TextType.MARKDOWN,
    TextType.BBCODE,
    TextType.PLAIN,
]
TEXT_CHOICES = [(tt.value, tt.name_lazy) for tt in TEXT_TYPES]


class StrainType(StrEnum):
    """
    Strain type enumeration.
    """
    UNKNOWN = "unknown"
    INDICA = "indica"
    INDICA_RUDERALIS = "indica_ruderalis"
    SATIVA = "sativa"
    SATIVA_RUDERALIS = "sativa_ruderalis"
    MOSTLY_INDICA = "mostly_indica"
    MOSTLY_SATIVA = "mostly_sativa"
    HYBRID = "hybrid"
    HYBRID_RUDERALIS = "hybrid_ruderalis"
    RUDERALIS = "ruderalis"

    @staticmethod
    def from_string(strain_str: str) -> 'StrainType':
        mapping = {
            "unknown": StrainType.UNKNOWN,
            "indica": StrainType.INDICA,
            "sativa": StrainType.SATIVA,
            "hybrid": StrainType.HYBRID,
            "indica_ruderalis": StrainType.INDICA_RUDERALIS,
            "sativa_ruderalis": StrainType.SATIVA_RUDERALIS,
            "hybrid_ruderalis": StrainType.HYBRID_RUDERALIS,
            "mostly_indica": StrainType.MOSTLY_INDICA,
            "mostly_sativa": StrainType.MOSTLY_SATIVA,
            "ruderalis": StrainType.RUDERALIS,
        }
        try:
            return mapping.get(strain_str.lower())
        except KeyError:
            raise ValueError(f"Unknown strain type: {strain_str}")

    @property
    def name_raw(self) -> str:
        mapping = {
            StrainType.UNKNOWN: _("unknown"),
            StrainType.INDICA: _("indica"),
            StrainType.SATIVA: _("sativa"),
            StrainType.HYBRID: _("indica/sativa"),
            StrainType.INDICA_RUDERALIS: _("indica/ruderalis"),
            StrainType.SATIVA_RUDERALIS: _("sativa/ruderalis"),
            StrainType.HYBRID_RUDERALIS: _("indica/sativa/ruderalis"),
            StrainType.MOSTLY_INDICA: _("mostly indica"),
            StrainType.MOSTLY_SATIVA: _("mostly sativa"),
            StrainType.RUDERALIS: _("ruderalis"),
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
    StrainType.UNKNOWN,
    StrainType.INDICA,
    StrainType.SATIVA,
    StrainType.RUDERALIS,
    StrainType.MOSTLY_INDICA,
    StrainType.MOSTLY_SATIVA,
    StrainType.HYBRID,
    StrainType.INDICA_RUDERALIS,
    StrainType.SATIVA_RUDERALIS,
    StrainType.HYBRID_RUDERALIS,


]
STRAIN_TYPE_CHOICES = [(st.value, st.name_lazy) for st in STRAIN_TYPES]


class PermissionType(StrEnum):
    """
    Growlog permission type enumeration.
    """

    PUBLIC = "public"
    PRIVATE = "private"
    MEMBERS_ONLY = "members_only"
    FRIENDS_ONLY = "friends_only"

    @staticmethod
    def from_string(permission_str: str) -> 'PermissionType':
        mapping = {
            "public": PermissionType.PUBLIC,
            "private": PermissionType.PRIVATE,
            "members_only": PermissionType.MEMBERS_ONLY,
            "friends_only": PermissionType.FRIENDS_ONLY,
        }
        try:
            return mapping.get(permission_str.lower())
        except KeyError:
            raise ValueError(f"Unknown permission type: {permission_str}")

    @property
    def name_raw(self) -> str:
        mapping = {
            PermissionType.PUBLIC: _("public"),
            PermissionType.PRIVATE: _("private"),
            PermissionType.MEMBERS_ONLY: _("members only"),
            PermissionType.FRIENDS_ONLY: _("friends only"),
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


PERMISSION_TYPES = [
    PermissionType.FRIENDS_ONLY,
    PermissionType.MEMBERS_ONLY,
    PermissionType.PRIVATE,
    PermissionType.PUBLIC,
]
PERMISSION_CHOICES = [(pt.value, pt.name_lazy) for pt in PERMISSION_TYPES]


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
            SensorType.TEMPERATURE: _("temperature"),
            SensorType.HUMIDITY: _("humidity"),
            SensorType.SOIL_MOISTURE: _("soil moisture"),
            SensorType.LIGHT_INTENSITY: _("light intensity"),
            SensorType.CO2_LEVEL: _("CO2 level"),
            SensorType.PH: _("pH"),
            SensorType.EC: _("electrical conductivity"),
            SensorType.TEMPERATURE_MEDIUM: _("medium temperature"),
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


SENSOR_TYPES = [
    SensorType.TEMPERATURE,
    SensorType.HUMIDITY,
    SensorType.SOIL_MOISTURE,
    SensorType.LIGHT_INTENSITY,
    SensorType.CO2_LEVEL,
    SensorType.PH,
    SensorType.EC,
    SensorType.TEMPERATURE_MEDIUM,
]
SENSOR_TYPE_CHOICES = [(st.value, st.name_lazy) for st in SENSOR_TYPES]


class LengthUnit(StrEnum):
    METRIC = 'metric'
    IMPERIAL = 'imperial'

    @staticmethod
    def from_string(string: str) -> "LengthUnit":
        mapping = {
            LengthUnit.METRIC.value: LengthUnit.METRIC,
            LengthUnit.IMPERIAL.value: LengthUnit.IMPERIAL,
        }

        try:
            return mapping[string.lower()]
        except KeyError:
            raise ValueError("Not a valid length unit!")

    @property
    def name_raw(self) -> str:
        mapping = {
            LengthUnit.METRIC: _("metric"),
            LengthUnit.IMPERIAL: _("imperial"),
        }
        return mapping[self]

    @property
    def name_lazy(self):
        return gettext_lazy(self.name_raw)

    @property
    def name(self):
        return gettext(self.name_raw)

    def __str__(self):
        return self.value

    @property
    def __repr__(self):
        return f"<LengthUnits: {self.value.upper()}>"


LENGTH_UNITS = [
    LengthUnit.METRIC,
    LengthUnit.IMPERIAL,
]
LENGTH_UNIT_CHOICES = [(lu.value, lu.name_lazy) for lu in LENGTH_UNITS]


class TemperatureUnit(StrEnum):
    CELCIUS = "C"
    FAHRENHEIT = "F"
    KELVIN = "K"

    @staticmethod
    def from_string(string: str) -> "TemperatureUnit":
        mapping = {
            'C': TemperatureUnit.CELCIUS,
            'CELCIUS': TemperatureUnit.CELCIUS,
            'F': TemperatureUnit.FAHRENHEIT,
            'FAHRENHEIT': TemperatureUnit.FAHRENHEIT,
            'K': TemperatureUnit.KELVIN,
            'KELVIN': TemperatureUnit.KELVIN,
        }
        try:
            return mapping[string.upper()]
        except KeyError:
            raise ValueError("Not a valid temperature unit!")

    @property
    def name_raw(self) -> str:
        mapping = {
            TemperatureUnit.CELCIUS: _("Celcius"),
            TemperatureUnit.FAHRENHEIT: _("Fahrenheit"),
            TemperatureUnit.KELVIN: _("Kelvin"),
        }
        return mapping[self]

    @property
    def name_lazy(self):
        return gettext_lazy(self.name_raw)

    @property
    def name(self) -> str:
        return gettext(self.name_raw)

    @property
    def unit(self):
        return self.value

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"<TemperatureUnit: {self.name_raw.upper()}>"


TEMPERATURE_UNITS = [
    TemperatureUnit.CELCIUS,
    TemperatureUnit.FAHRENHEIT,
    TemperatureUnit.KELVIN,
]
TEMPERATURE_UNIT_CHOICES = [(tu.value, tu.name_lazy) for tu in TEMPERATURE_UNITS]


class PermissionCode(IntEnum):
    ALLOW = 1
    CONTINUE = 2
    RESTRICT = 3
    RAISE_EXCEPTION = 4
