from django import forms
from django.utils.translation import gettext_lazy as _  # noqa: F401
from ..growapi.models import (  # noqa: F401
    Growlog,
    GrowlogEntry,
    GrowlogEntryImage,
    GrowlogStrain,
    Breeder,
    Strain,
    Location,
)
from django.db.models import Count


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


class StrainModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class GrowlogAddStrainForm(forms.Form):

    breeder_filter = forms.CharField(
        label=_("Breeder filter"),
        required=False,
    )

    breeder = forms.ModelChoiceField(
        queryset=Breeder.objects.annotate(
            strains_count=Count('strains')
        ).filter(strains_count__gt=0).order_by('name'),
        label=_("Breeder"),
        required=False
    )

    strain = StrainModelChoiceField(
        queryset=Strain.objects.all(),
        label=_("Strain"),
        required=True
    )

    quantity = forms.IntegerField(
        label=_("Quantity"),
        required=True,
        min_value=1,
        initial=1
    )

    is_grown_from_seed = forms.BooleanField(
        label=_("Grown from seed"),
        required=False,
        initial=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class GrowlogQuantityForm(forms.Form):

    quantity = forms.IntegerField(
        label=_("Quantity"),
        required=True,
        initial=1
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LocationModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj: Location):
        return f"{obj.name} ({obj.location_type.name})"


class GrowlogEntryForm(forms.ModelForm):

    class Meta:
        model = GrowlogEntry
        fields = [
            'content_type_data',
            'content',
            'location',
        ]


class GrowlogDeleteForm(forms.Form):
    confirm = forms.BooleanField(
        label=_("Confirm deletion"),
        required=True,
    )


class GrowlogEntryImageForm(forms.ModelForm):

    class Meta:
        model = GrowlogEntryImage
        fields = [
            'image',
            'description_type_data',
            'description',
        ]
