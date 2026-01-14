# marches/urls.py
from django.urls import path
from . import views

app_name = 'marches'

urlpatterns = [
    path('description/<int:marche_detaille_id>/', views.description_view, name='description'),
]