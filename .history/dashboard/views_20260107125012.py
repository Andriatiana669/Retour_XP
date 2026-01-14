# dashboard/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from marches.models import MarcheGlobal, MarcheDetaille, EtatAffaire
from django import forms
from authentification.models import Profile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

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

@login_required
def ajouter_marche_view(request, marche_global_id):
    marche_global = get_object_or_404(MarcheGlobal, id=marche_global_id)
    if request.method == 'POST':
        form = MarcheDetailleForm(request.POST)
        if form.is_valid():
            marche = form.save(commit=False)
            marche.marche_global = marche_global
            # valeurs « vides » pour les champs non saisis
            marche.titre        = ''
            marche.objet        = ''
            marche.nom_client   = ''
            marche.date_retour  = None
            marche.description  = ''
            marche.save()
            return redirect('dashboard:liste_marche', marche_global_id=marche_global.id)
    else:
        form = MarcheDetailleForm()
    return render(request, 'dashboard/ajouter_marche.html',
                  {'form': form, 'marche_global': marche_global})


@login_required
def change_etat_view(request, pk):
    """AJAX : change l'état d'un marché détaillé"""
    marche = get_object_or_404(MarcheDetaille, pk=pk)
    if request.method == 'POST':
        data = json.loads(request.body)
        etat_id = data.get('etat')
        marche.etat_affaire = EtatAffaire.objects.filter(pk=etat_id).first() or None
        marche.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'bad'}, status=400)