# marches/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import MarcheDetaille

@login_required
def description_view(request, marche_detaille_id):
    marche_detaille = get_object_or_404(MarcheDetaille, id=marche_detaille_id)
    cartes = marche_detaille.cartes.all()
    
    context = {
        'marche_detaille': marche_detaille,
        'cartes': cartes
    }
    return render(request, 'marches/description.html', context)