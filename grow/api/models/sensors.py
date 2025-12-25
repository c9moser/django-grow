"""
Sensor models
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from ..enums import (
    SensorType,
    SENSOR_TYPES,
)

class Sensor(models.Model):
    key = models.SlugField(_("key"),
                           max_length=255,
                           unique=True)
    name = models.CharField(_("name"),
                            max_length=255)
    location = models.ForeignKey('Location',
                                 on_delete=models.CASCADE,
                                 related_name='sensors',
                                 verbose_name=_("location"))

    sensor_type_data = models.CharField(_("sensor type"),
                                        max_length=50,
                                        choices=[
                                            (st.value, st.name_lazy)
                                            for st in SENSOR_TYPES
                                        ])

    class Meta:
        db_table = "grow_sensor"


class SensorReading(models.Model):
    sensor = models.ForeignKey(Sensor,
                               on_delete=models.CASCADE,
                               related_name='readings',
                               verbose_name=_("readings"))
    timestamp = models.DateTimeField(_("timestamp"),
                                     auto_now_add=True)
    value = models.DecimalField(_("value"))

    class Meta:
        db_table = "grow_sensor_reading"
        ordering = ['-timestamp']
