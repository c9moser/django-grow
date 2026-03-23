from datetime import date

from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.db.models import Count

from ..growapi.models import (
    Breeder,
    Strain,
    StrainImage,
    BreederTranslation,
    StrainTranslation,
    StrainUserComment,
)
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        today = date.today()
        self.fields['purchased_on_year'].initial = today.year
        self.fields['purchased_on_month'].initial = today.month
        self.fields['purchased_on_day'].initial = today.day

    quantity = forms.IntegerField(
        min_value=0,
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


class StrainModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class StrainAddToStock2Form(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        today = date.today()
        self.fields['purchased_on_year'].initial = today.year
        self.fields['purchased_on_month'].initial = today.month
        self.fields['purchased_on_day'].initial = today.day

        if 'breeder_filter' in self.data and self.data['breeder_filter']:
            breeders = Breeder.objects.annotate(
                strains_count=Count('strains')
            ).filter(
                strains_count__gt=0,
                name__icontains=self.data['breeder_filter']
            ).order_by('name')

        else:
            breeders = Breeder.objects.annotate(
                strains_count=Count('strains')
            ).filter(strains_count__gt=0).order_by('name')

        if 'breeder' in self.data and self.data['breeder']:
            try:
                breeder = breeders.get(id=self.data['breeder'])
            except Breeder.DoesNotExist:
                if breeders:
                    breeder = breeders.first()
                else:
                    breeder = None
        else:
            breeder = breeders.first() if breeders else None

        self.fields['breeder'].queryset = breeders
        self.fields['breeder'].initial = breeder
        self.fields['breeder'].value = breeder.id if breeder else None

        if breeder:
            if 'strain_filter' in self.data and self.data['strain_filter']:
                strains = breeder.strains.filter(
                    name__icontains=self.data['strain_filter']
                ).order_by('name')
            else:
                strains = breeder.strains.all().order_by('name')

            if 'strain' in self.data and self.data['strain']:
                try:
                    strain = strains.get(id=self.data['strain'])
                except Strain.DoesNotExist:
                    strain = strains.first() if strains else None
            else:
                strain = strains.first() if strains else None

            self.fields['strain'].queryset = strains
            self.fields['strain'].initial = strain
            # self.data['strain'] = strain.id if strain else None
        else:
            self.fields['strain'].queryset = Strain.objects.none()
            self.fields['strain'].initial = None
            # self.data['strain'] = None

    breeder_filter = forms.CharField(
        max_length=255,
        required=False,
        label=_("Filter breeders...")
    )
    breeder = forms.ModelChoiceField(
        queryset=Breeder.objects.annotate(
            strains_count=Count('strains')
        ).filter(strains_count__gt=0).order_by('name'),
        required=True,
        label=_("Breeder")
    )

    strain_filter = forms.CharField(
        max_length=255,
        required=False,
        label=_("Filter strains...")
    )
    strain = StrainModelChoiceField(
        queryset=Strain.objects.none(),
        label=_("Strain"),
        required=False,
    )

    quantity = forms.IntegerField(
        min_value=1,
        max_value=1000000000,
        required=True,
        initial=1,
        label=_("Quantity")
    )

    strain_type = forms.ChoiceField(
        choices=[
            ('feminized', _("Feminized")),
            ('regular', _("Regular")),
        ],
        widget=forms.RadioSelect,
        required=True,
        initial="feminized"
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


class StrainCommentForm(forms.ModelForm):
    class Meta:
        model = StrainUserComment
        fields = [
            "language_code",
            "comment_type_data",
            "comment",
        ]
