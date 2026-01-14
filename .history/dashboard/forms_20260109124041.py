from django import forms
from marches.models import MarcheDetaille
from authentification.models import Profile
from marches.models import NomClient, Prestation

class MarcheDetailleAdminForm(forms.ModelForm):
    class Meta:
        model = MarcheDetaille
        fields = '__all__'

    resp_marche = forms.ModelMultipleChoiceField(
        queryset=Profile.objects.filter(user__is_active=True),
        widget=forms.SelectMultiple(attrs={'size': 5}),
        required=False,
        label="Responsables"
    )
    nom_client = forms.ModelMultipleChoiceField(
        queryset=NomClient.objects.all(),
        widget=forms.SelectMultiple(attrs={'size': 5}),
        required=False,
        label="Clients"
    )
    prestation = forms.ModelMultipleChoiceField(
        queryset=Prestation.objects.all(),
        widget=forms.SelectMultiple(attrs={'size': 5}),
        required=False,
        label="Prestations"
    )