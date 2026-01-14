# authentification/urls.py
from django.urls import path
from . import views

app_name = 'authentification'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.custom_logout, name='logout'),   # ← nouvelle ligne
]