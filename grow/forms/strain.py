from django import forms
from django.utils.translation import gettext_lazy as _
from ..api.models import Strain


class StrainForm(forms.ModelForm):
    flowering_time_unit = forms.ChoiceField(
        choices=[
            ('d', _("Days")),
            ('w', _("Weeks")),
        ],
        widget=forms.RadioSelect,
        required=True,
        initial="d"
    )

    class Meta:
        model = Strain
        fields = [
            'slug',
            'name',
            'description_type_data',
            'description',
            'is_regular',
            'is_feminized',
            'is_automatic',
            'genetics_data',
            'flowering_time_days',
            'logo_url',
            'logo_image',
            'strain_url',
            'seedfinder_url',
        ]
