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
            'permission_data',
            'description_type_data',
            'description',
            'notes_type_data',
            'notes',
        ]


class GrowlogStrainForm(forms.ModelForm):
    class Meta:
        model = GrowlogStrain
        fields = ['strain', 'quantity', 'is_grown_from_seed']


class GrowlogSeedsFromStockForm(forms.Form):

    strain_filter = forms.CharField(
        label=_("Strain filter"),
        required=False,
    )

    seeds_in_stock = forms.ModelChoiceField(
        queryset=None,
        label=_("Seeds in stock"),
        required=True
    )

    quantity = forms.IntegerField(
        label=_("Quantity"),
        required=True,
        min_value=1,
        initial=1
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['seeds_in_stock'].queryset = user.seeds_in_stock.filter(
            quantity__gt=0
        ).order_by(
            'strain__name',
            'strain__breeder__name'
        )
        self.fields['seeds_in_stock'].initial = self.fields['seeds_in_stock'].queryset.first()


class GrowlogNotesForm(forms.ModelForm):
    class Meta:
        model = Growlog
        fields = [
            'notes_type_data',
            'notes',
        ]


class GrowlogDescriptionForm(forms.ModelForm):
    class Meta:
        model = Growlog
        fields = [
            'description_type_data',
            'description',
        ]


class GrowlogStrainDeleteForm(forms.ModelForm):
    class Meta:
        model = GrowlogStrain
        fields = []


class GrowlogQuantityForm(forms.Form):

    quantity = forms.IntegerField(
        label=_("Quantity"),
        required=True,
        initial=1
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
