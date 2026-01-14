# dashboard/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from marches.models import MarcheGlobal, MarcheDetaille

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