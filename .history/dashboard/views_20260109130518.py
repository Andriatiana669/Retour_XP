# dashboard/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from marches.models import MarcheGlobal, MarcheDetaille, EtatAffaire
from django import forms
from .forms import MarcheDetailleAdminForm
from authentification.models import Profile
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

@login_required
def dashboard_view(request):
    marches_globaux = MarcheGlobal.objects.all()
    context = {
        'marches_globaux': marches_globaux
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def liste_marche_view(request, marche_global_id):
    marche_global   = get_object_or_404(MarcheGlobal, id=marche_global_id)
    marches_detailles = MarcheDetaille.objects.filter(marche_global=marche_global)
    etats             = EtatAffaire.objects.all()          # <-- manquant
    return render(request, 'dashboard/liste_marche.html',
                  {'marche_global': marche_global,
                   'marches_detailles': marches_detailles,
                   'etats': etats})                        # <-- renvoyé


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
            # champs masqués déjà remplis
            marche.titre = ''
            marche.description = ''
            marche.objet = ''
            marche.date_retour = None
            marche.save()
            # Important : sauvegarder les ManyToMany
            form.save_m2m()
            
            # Redirection vers la liste des marchés du marche_global
            return redirect('dashboard:liste_marche', marche_global_id=marche_global.id)
    else:
        form = MarcheDetailleForm()
    
    return render(request, 'dashboard/ajouter_marche.html', {
        'form': form,
        'marche_global': marche_global
    })



@login_required
def change_etat_view(request, pk):
    if request.method == 'POST':
        data = json.loads(request.body)
        etat_id = data.get('etat')
        marche = get_object_or_404(MarcheDetaille, pk=pk)
        marche.etat_affaire = EtatAffaire.objects.filter(pk=etat_id).first() or None
        marche.save()
        return JsonResponse({
            'status': 'ok',
            'date_maj': timezone.localtime(marche.date_maj).strftime('%d/%m/%Y %H:%M')
        })
    return JsonResponse({'status': 'bad'}, status=400)

@login_required
def modifier_marche_view(request, pk):
    marche = get_object_or_404(MarcheDetaille, pk=pk)
    if request.method == 'POST':
        form = MarcheDetailleAdminForm(request.POST, instance=marche)
        if form.is_valid():
            form.save()
            return redirect('dashboard:liste_marche', marche_global_id=marche.marche_global.id)
    else:
        form = MarcheDetailleAdminForm(instance=marche)
    return render(request, 'dashboard/ajouter_marche.html',
                  {'form': form, 'marche_global': marche.marche_global})

@login_required
def supprimer_marche_view(request, pk):
    marche = get_object_or_404(MarcheDetaille, pk=pk)
    marche_global_id = marche.marche_global_id
    marche.delete()
    return redirect('dashboard:liste_marche', marche_global_id=marche_global_id)