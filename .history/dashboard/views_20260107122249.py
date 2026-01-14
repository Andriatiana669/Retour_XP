# dashboard/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from marches.models import MarcheGlobal, MarcheDetaille, EtatAffaire
from django import forms
from authentification.models import Profile

@login_required
def dashboard_view(request):
    marches_globaux = MarcheGlobal.objects.all()
    context = {
        'marches_globaux': marches_globaux
    }
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def liste_marche_view(request, marche_global_id):
    marche_global = get_object_or_404(MarcheGlobal, id=marche_global_id)
    marches_detailles = MarcheDetaille.objects.filter(marche_global=marche_global)
    
    context = {
        'marche_global': marche_global,
        'marches_detailles': marches_detailles
    }
    return render(request, 'dashboard/liste_marche.html', context)


# ---------- Formulaire rapide ----------
class MarcheDetailleForm(forms.ModelForm):
    class Meta:
        model  = MarcheDetaille
        fields = ['nom_marche', 'resp_marche', 'etat_affaire']

    resp_marche = forms.ModelChoiceField(
        queryset=Profile.objects.filter(user__is_active=True),
        label="Responsable du marché"
    )
    etat_affaire = forms.ModelChoiceField(
        queryset=EtatAffaire.objects.all(),
        required=False,
        label="État d’affaire"
    )
    date_retour = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Date de retour"
    )

@login_required
def ajouter_marche_view(request, marche_global_id):
    marche_global = get_object_or_404(MarcheGlobal, id=marche_global_id)
    if request.method == 'POST':
        form = MarcheDetailleForm(request.POST)
        if form.is_valid():
            marche = form.save(commit=False)
            marche.marche_global = marche_global
            marche.save()
            return redirect('dashboard:liste_marche', marche_global_id=marche_global.id)
    else:
        form = MarcheDetailleForm()
    return render(request, 'dashboard/ajouter_marche.html',
                  {'form': form, 'marche_global': marche_global})