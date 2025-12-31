from django import forms
from django.utils.translation import gettext_lazy as L_


class DeleteWithSlugForm(forms.Form):
    slug = forms.SlugField(allow_unicode=False,
                           required=True,
                           label=L_("Slug"))
