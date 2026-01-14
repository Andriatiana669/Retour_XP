import django.forms as forms
from marches.models import EtatAffaire, MarcheDetaille
from authentification.models import Profile

class MarcheDetailleForm(forms.ModelForm):
    class Meta:
        model  = MarcheDetaille
        fields = ['nom_marche', 'resp_marche', 'etat_affaire']

    resp_marche = forms.ModelChoiceField(
        queryset=Profile.objects.filter(user__is_active=True),
        label="Responsable du marché")
    etat_affaire = forms.ModelChoiceField(
        queryset=EtatAffaire.objects.all(),
        required=False,
        label="État d’affaire")