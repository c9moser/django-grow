from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now

from ..growapi.models import Strain, StrainImage, BreederTranslation, StrainTranslation
from ..enums import TextType, TEXT_CHOICES


def get_year_choices(n=20):

    today = now().date()

    return [
        (y, str(y)) for y in sorted(range(today.year - n, today.year + 1), reverse=True)
    ]


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
            'is_discontinued',
            'genotype_data',
            'flowering_time_days',
            'logo_url',
            'logo_image',
            'strain_url',
            'seedfinder_url',
        ]


class StrainAddToStockForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        max_value=1000000000,
        required=True,
        label=_("Quantity")
    )
    purchased_on_year = forms.ChoiceField(
        label=_("Purchased on Year"),
        required=False,
        choices=get_year_choices(10),
        initial=now().year
    )

    purchased_on_month = forms.ChoiceField(
        label=_("Puchased on Month"),
        required=False,
        choices=[(i, str(i)) for i in range(1, 13)],
        initial=now().month
    )
    purchased_on_day = forms.ChoiceField(
        label=_("Purchased on Day"),
        required=False,
        choices=[(i, str(i)) for i in range(1, 32)],
        initial=now().day
    )

    notes_type = forms.ChoiceField(
        choices=TEXT_CHOICES,
        initial=TextType.MARKDOWN.value,
        required=False)
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(),
        label=_("Notes"),
    )


class StrainRemoveFromStockForm(forms.Form):
    quantity = forms.IntegerField(
        label=_("Quantity")
    )


class BreederFilterForm(forms.Form):
    search_query = forms.CharField(

        required=False,
        max_length=255,
        label=_("Filter breeders..."),
    )


class StrainSearchForm(forms.Form):
    search_query = forms.CharField(
        required=True,
        max_length=255,
        label=_("Search strains..."),
    )


class StrainFilterForm(forms.Form):
    search_query = forms.CharField(
        required=False,
        max_length=255,
        label=_("Filter strains..."),
    )


class StrainImageUploadForm(forms.ModelForm):
    class Meta:
        model = StrainImage
        fields = [
            'image',
            'caption',
            'description_type_data',
            'description',
        ]


class BreederTranslationForm(forms.ModelForm):
    class Meta:
        model = BreederTranslation
        fields = [
            'language_code',
            'name',
            'breeder_url',
            'seedfinder_url',
            'description_type_data',
            'description',
        ]


class StrainTranslationForm(forms.ModelForm):
    class Meta:
        model = StrainTranslation
        fields = [
            'language_code',
            'name',
            'strain_url',
            'seedfinder_url',
            'description_type_data',
            'description',
        ]
