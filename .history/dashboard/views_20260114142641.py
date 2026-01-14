# dashboard/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from marches.models import MarcheGlobal, MarcheDetaille, EtatAffaire, NomMarche, Prestation, NomClient, Carte
from django import forms
from .forms import MarcheDetailleAdminForm
from authentification.models import Profile
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import datetime
import pandas as pd
from django.http import HttpResponse
from django.db.models import Q, Value, CharField, Prefetch
from django.urls import reverse


@login_required
def dashboard_view(request):
    # on précharge tout ce qui servira à la recherche
    marches_globaux = (
        MarcheGlobal.objects
        .prefetch_related(
            Prefetch(
                'marches_detailles',
                queryset=(
                    MarcheDetaille.objects
                    .select_related('nom_marche', 'etat_affaire')
                    .prefetch_related(
                        'resp_marche__user',
                        'nom_client',
                        'prestation'
                    )
                )
            ),
            'marches_detailles__cartes__solution',
            'marches_detailles__cartes__nom_client'
        )
    )

    # construction d’un dictionnaire « plat » indexé par l’id du GLOBAL
    data = {}
    for mg in marches_globaux:
        detail_data = []
        for md in mg.marches_detailles.all():
            carte_data = []
            for c in md.cartes.all():
                carte_data.append({
                    'titre': c.titre,
                    'objet': c.objet or '',
                    'contenu': c.contenu,
                    'solution': str(c.solution) if c.solution else '',
                    'nom_dossier': c.nom_dossier or '',
                    'client_carte': str(c.nom_client) if c.nom_client else '',
                })
            detail_data.append({
                'id': md.id,
                'nom_marche': str(md.nom_marche),
                'titre': md.titre,
                'objet': md.objet or '',
                'description': md.description or '',
                'resp': ' '.join(str(r.user) for r in md.resp_marche.all()),
                'clients': ' '.join(str(c) for c in md.nom_client.all()),
                'prestations': ' '.join(str(p) for p in md.prestation.all()),
                'cartes': carte_data,
                
            })
        data[mg.id] = detail_data

    return render(request, 'dashboard/dashboard.html', {
        'marches_globaux': marches_globaux,
        'search_data': data,  # on passe ça au template
    })


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

# ---------- FORMULAIRE AJOUT MARCHÉ DÉTAILLÉ ----------
class MarcheDetailleFormAdmin(forms.ModelForm):
    class Meta:
        model = MarcheDetaille
        fields = ['nom_marche', 'resp_marche', 'etat_affaire', 'nom_client', 'prestation']

    resp_marche = forms.ModelMultipleChoiceField(
        queryset=Profile.objects.filter(user__is_active=True),
        label="Responsable du marché",
        required=False
    )
    nom_client = forms.ModelMultipleChoiceField(
        queryset=NomClient.objects.all(),
        label="Client",
        required=False
    )
    prestation = forms.ModelMultipleChoiceField(
        queryset=Prestation.objects.all(),
        label="Prestations",
        required=False
    )


def responsable_required(view_func):
    def wrapper(request, *args, **kwargs):
        profile = getattr(request.user, 'profile', None)
        if not profile or not profile.est_responsable:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@responsable_required
def ajouter_marche_view(request, marche_global_id):
    from marches.models import MarcheGlobal

    marche_global = get_object_or_404(MarcheGlobal, id=marche_global_id)

    if request.method == 'POST':
        form = MarcheDetailleFormAdmin(request.POST)
        if form.is_valid():
            marche = form.save(commit=False)
            marche.marche_global = marche_global

            # Valeurs vides pour les champs que nous n'utilisons pas ici
            marche.titre = ''
            marche.objet = ''
            marche.description = ''
            marche.date_retour = None
            marche.save()              # Sauvegarde de l'objet principal
            form.save_m2m()            # Sauvegarde des ManyToMany

            return redirect('dashboard:liste_marche', marche_global_id=marche_global.id)
    else:
        form = MarcheDetailleFormAdmin()

    return render(request, 'dashboard/ajouter_marche.html', {
        'form': form,
        'marche_global': marche_global
    })



@login_required
@responsable_required
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
@responsable_required
def modifier_marche_view(request, pk):
    marche = get_object_or_404(MarcheDetaille, pk=pk)

    if request.method == 'POST':
        form = MarcheDetailleFormAdmin(request.POST, instance=marche)
        if form.is_valid():
            marche = form.save(commit=False)

            # Les champs non utilisés restent vides
            marche.titre = ''
            marche.objet = ''
            marche.description = ''
            marche.date_retour = None
            marche.save()
            form.save_m2m()  # sauvegarde des ManyToMany

            return redirect('dashboard:liste_marche', marche_global_id=marche.marche_global.id)
    else:
        form = MarcheDetailleFormAdmin(instance=marche)

    return render(request, 'dashboard/ajouter_marche.html', {  # Réutilisation du même template
        'form': form,
        'marche_global': marche.marche_global,
        'is_edit': True  # facultatif, si tu veux afficher "Modifier" au lieu de "Ajouter"
    })

@login_required
@responsable_required
def supprimer_marche_view(request, pk):
    marche = get_object_or_404(MarcheDetaille, pk=pk)
    # TODO : A remplacer ito
    # marche_global_id = marche.marche_global_id
    marche_global_id = marche.marche_global.id
    marche.delete()
    return redirect('dashboard:liste_marche', marche_global_id=marche_global_id)



@login_required
@responsable_required
def export_global_xlsx(request, marche_global_id):
    mg = get_object_or_404(MarcheGlobal, id=marche_global_id)
    cartes = Carte.objects.filter(
        marche_detaille__marche_global=mg
    ).select_related('solution', 'nom_client')

    df = pd.DataFrame([
        {
            'Titre': str(c.titre or ''),
            'Objet': str(c.objet or ''),
            'Client': str(c.nom_client or ''),
            'Date retour': c.date_retour,
            'Solution': str(c.solution or ''),
            'Demande démarche': 'Oui' if c.solution and c.solution.demande_demarche else 'Non',
            'Démarche solution': str(c.demarche_solution or ''),
            'Nom dossier': str(c.nom_dossier or ''),
            'Date livraison': pd.NaT if c.date_livraison is None else pd.Timestamp(c.date_livraison),
            'Date MAJ': pd.Timestamp(timezone.make_naive(c.date_maj) if c.date_maj.tzinfo else c.date_maj)
        }
        for c in cartes
    ])

    filename = f"global_{mg.nom}_{datetime.now():%Y%m%d_%H%M}.xlsx"
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    df.to_excel(response, index=False, engine='openpyxl')
    return response