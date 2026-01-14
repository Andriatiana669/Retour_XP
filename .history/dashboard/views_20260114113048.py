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
from django.db.models import Q, Value, CharField
from django.urls import reverse


@login_required
def dashboard_view(request):
    q = request.GET.get('q', '').strip()
    type_filter = request.GET.get('type', 'all')          # all / global / detaille / carte

    # 1) Marchés globaux
    mg_qs = MarcheGlobal.objects.annotate(
        obj_type=Value('global', output_field=CharField()),
        url=Value('', output_field=CharField())   # on le remplit plus bas
    )
    # 2) Marchés détaillés
    md_qs = MarcheDetaille.objects.select_related('marche_global', 'etat_affaire').annotate(
        obj_type=Value('detaille', output_field=CharField()),
        url=Value('', output_field=CharField())
    )
    # 3) Cartes
    c_qs = Carte.objects.select_related('marche_detaille__marche_global', 'solution', 'nom_client').annotate(
        obj_type=Value('carte', output_field=CharField()),
        url=Value('', output_field=CharField())
    )

    # Filtre texte
    if q:
        mg_qs = mg_qs.filter(Q(nom__icontains=q) | Q(description__icontains=q))
        md_qs = md_qs.filter(
            Q(titre__icontains=q) |
            Q(objet__icontains=q) |
            Q(description__icontains=q) |
            Q(matricule__icontains=q)
        )
        c_qs = c_qs.filter(
            Q(titre__icontains=q) |
            Q(objet__icontains=q) |
            Q(contenu__icontains=q) |
            Q(nom_client__nom__icontains=q)
        )

    # Filtre type
    if type_filter == 'global':
        results = mg_qs
    elif type_filter == 'detaille':
        results = md_qs
    elif type_filter == 'carte':
        results = c_qs
    else:  # 'all'
        results = mg_qs.union(md_qs, c_qs)

    # On ajoute l’URL de destination et un titre lisible
    final = []
    for obj in results:
        if obj.obj_type == 'global':
            obj.title = obj.nom
            obj.subtitle = f"{obj.nombre_projet} projet(s)"
            obj.url = reverse('dashboard:liste_marche', args=[obj.id])
        elif obj.obj_type == 'detaille':
            obj.title = obj.titre or str(obj)
            obj.subtitle = f"Marché global : {obj.marche_global.nom}"
            obj.url = reverse('dashboard:liste_marche', args=[obj.marche_global_id]) + f"#md-{obj.id}"
        else:  # carte
            obj.title = obj.titre
            obj.subtitle = f"Carte – marché : {obj.marche_detaille.titre}"
            obj.url = reverse('marches:voir_carte', args=[obj.id])
        final.append(obj)

    return render(request, 'dashboard/dashboard.html', {
        'results': final,
        'q': q,
        'type_filter': type_filter
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