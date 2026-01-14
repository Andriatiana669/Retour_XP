# marches/urls.py
from django.urls import path
from . import views

app_name = 'marches'

urlpatterns = [
    path('description/<int:marche_detaille_id>/',       views.description_view, name='description'),

    # Cartes
    path('carte/ajouter/<int:marche_detaille_id>/',     views.ajouter_carte_view,   name='ajouter_carte'),
    path('carte/voir/<int:carte_id>/',                  views.voir_carte_view,      name='voir_carte'),
    path('carte/modifier/<int:carte_id>/',              views.modifier_carte_view,  name='modifier_carte'),
    path('carte/supprimer/<int:carte_id>/',             views.supprimer_carte_view, name='supprimer_carte'),
    path('carte/download/word/<int:carte_id>/',         views.download_word_view, name='download_word'),
]