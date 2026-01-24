from django import forms
from ..growapi.models.location import Location
from django.utils.translation import gettext_lazy as L_
from ..growapi.enums import GrowLightType, GROW_LIGHT_CHOICES


class LocationForm(forms.ModelForm):
    width = forms.IntegerField(
        label=L_('Width'),
        required=False,
        help_text=L_('Width of the location in centimeters.'),
    )

    height = forms.IntegerField(
        label=L_('Height'),
        required=False,
        help_text=L_('Height of the location in centimeters.'),
    )

    depth = forms.IntegerField(
        label=L_('Depth'),
        required=False,
        help_text=L_('Depth of the location in centimeters.'),
    )

    light_type = forms.ChoiceField(
        label=L_('Light Type'),
        required=False,
        choices=GROW_LIGHT_CHOICES,
        initial=GrowLightType.LED.value,
        help_text=L_('Type of lighting used in the location.'),
    )

    light_power_consumption = forms.IntegerField(
        label=L_('Light Power Consumption (Watts)'),
        required=False,
        help_text=L_('Power consumption of the lighting in Watts.'),
        initial=0,
    )

    ventilation_power_consumption = forms.IntegerField(
        label=L_('Ventilation Power Consumption (Watts)'),
        required=False,
        help_text=L_('Power consumption of the ventilation system in Watts.'),
        initial=0,
    )

    ventilation_intensity = forms.IntegerField(
        label=L_('Ventilation Intensity (Cubic Meters per Hour)'),
        required=False,
        help_text=L_('Ventilation intensity in cubic meters per hour.'),
        initial=0,
    )

    longitude = forms.DecimalField(
        label=L_('Longitude'),
        required=False,
        max_digits=9,
        decimal_places=6,
        help_text=L_('Longitude coordinate of the location.'),
    )

    latitude = forms.DecimalField(
        label=L_('Latitude'),
        required=False,
        max_digits=9,
        decimal_places=6,
        help_text=L_('Latitude coordinate of the location.'),
    )

    class Meta:
        model = Location
        fields = [
            'name',
            'key',
            'location_type_data',
            'permission_data',
            'description',
            'description_type_data',
        ]


class LocationTypeChangeForm(forms.Form):
    width = forms.IntegerField(
        label=L_('Width'),
        required=False,
        help_text=L_('Width of the location in centimeters.'),
    )

    height = forms.IntegerField(
        label=L_('Height'),
        required=False,
        help_text=L_('Height of the location in centimeters.'),
    )

    depth = forms.IntegerField(
        label=L_('Depth'),
        required=False,
        help_text=L_('Depth of the location in centimeters.'),
    )

    light_type = forms.ChoiceField(
        label=L_('Light Type'),
        required=False,
        choices=GROW_LIGHT_CHOICES,
        initial=GrowLightType.LED.value,
        help_text=L_('Type of lighting used in the location.'),
    )

    light_power_consumption = forms.IntegerField(
        label=L_('Light Power Consumption (Watts)'),
        required=False,
        help_text=L_('Power consumption of the lighting in Watts.'),
        initial=0,
    )

    ventilation_power_consumption = forms.IntegerField(
        label=L_('Ventilation Power Consumption (Watts)'),
        required=False,
        help_text=L_('Power consumption of the ventilation system in Watts.'),
        initial=0,
    )

    ventilation_intensity = forms.IntegerField(
        label=L_('Ventilation Intensity (Cubic Meters per Hour)'),
        required=False,
        help_text=L_('Ventilation intensity in cubic meters per hour.'),
        initial=0,
    )

    longitude = forms.DecimalField(
        label=L_('Longitude'),
        required=False,
        max_digits=9,
        decimal_places=6,
        help_text=L_('Longitude coordinate of the location.'),
    )

    latitude = forms.DecimalField(
        label=L_('Latitude'),
        required=False,
        max_digits=9,
        decimal_places=6,
        help_text=L_('Latitude coordinate of the location.'),
    )


class DeleteLocationForm(forms.Form):
    pass  # Placeholder for future fields if needed
