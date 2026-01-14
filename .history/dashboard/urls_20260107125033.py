# dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('marche/<int:marche_global_id>/', views.liste_marche_view, name='liste_marche'),
    path('marche/<int:marche_global_id>/ajouter/', views.ajouter_marche_view, name='ajouter_marche'),
    path('marche/change-etat/<int:pk>/', views.change_etat_view, name='change_etat'),
    
]