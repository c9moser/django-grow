"""
Sensor models
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
import json
import bz2

from .. import settings

from ..enums import (
    SensorType,
    SENSOR_TYPE_CHOICES,
)
from .location import Location


class Sensor(models.Model):
    """
    A Sensor for growlogs.
    """

    #: The sensor lookup key
    key = models.SlugField(
        _("key"),
        max_length=255
    )
    #: The sensor name
    name = models.CharField(
        _("name"),
        max_length=255
    )

    #: The sensor owner
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    #: The location of the sensor
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='sensors',
        verbose_name=_("location")
    )

    #: The sensor type
    sensor_type_data = models.CharField(
        _("sensor type"),
        max_length=50,
        choices=SENSOR_TYPE_CHOICES,
        db_column='sensor_type'
    )

    @property
    def sensor_type(self) -> SensorType:
        return SensorType.from_string(self.sensor_type_data)

    @sensor_type.setter
    def sensor_type(self, st):
        self.sensor_type_data = SensorType.value

    class Meta:
        db_table = "grow_sensor"
        unique_together = [
            ('owner', 'key')
        ]


class SensorReading(models.Model):
    """
    The readings of the sensor.
    """

    #: The sensor the readings belong to
    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name='readings',
        verbose_name=_("readings")
    )

    #: The timestamp of the readings
    timestamp = models.DateTimeField(
        _("timestamp"),
        auto_now_add=True
    )
    value = models.DecimalField(
        _("value"),
        decimal_places=2,
        max_digits=8
    )

    class Meta:
        db_table = "grow_sensor_reading"
        ordering = ['-timestamp']


class SensorReadingDay(models.Model):
    """The readings for a day."""
    date = models.DateField(
        _("Date"),
        auto_now_add=True
    )

    readings_data = models.BinaryField(
        _("The readings"),
        db_column='readings'
    )

    _readings_comrepssed = models.BooleanField(
        _("Compressed readings"),
        db_column='readings_compressed',
        default=settings.GRC_SENSOR_READINGS_PER_DAY_COMPRESSED
    )

    @property
    def readings(self) -> list[dict]:
        if self._readings_comrepssed:
            data = bz2.decompress(self.readings_data).decode('utf-8')
        else:
            data = self.readings.decode('utf-8')

        return json.loads(data)

    @readings.setter
    def readings(self, readings: list[dict]):
        data = json.dumps(readings, ensure_ascii=False).encode('utf-8')

        if settings.GRC_SENSOR_READINGS_PER_DAY_COMPRESSED:
            self.readings_data = bz2.compress(data)
        else:
            self.readings_data = data
