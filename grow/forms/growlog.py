from django import forms
from django.utils.translation import gettext_lazy as _  # noqa: F401
from ..growapi.models import (  # noqa: F401
    Growlog,
    GrowlogEntry,
    GrowlogEntryImage,
    GrowlogStrain,
)


class GrowlogForm(forms.ModelForm):
    class Meta:
        model = Growlog
        fields = [
            'name',
            'description_type_data',
            'description',
            'notes_type_data',
            'notes',
        ]


class GrowlogStrainForm(forms.ModelForm):
    class Meta:
        model = GrowlogStrain
        fields = ['strain', 'quantity', 'is_grown_from_seed']


GrowlogStrainFormSet = forms.inlineformset_factory(
    Growlog,
    GrowlogStrain,
    form=GrowlogStrainForm,
    extra=0,
    can_delete=True
)
