# authentification/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from .models import Profile
import uuid

def login_view(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')

        if user_type == 'simple':
            # Connexion anonyme
            username = f"anonymous_{uuid.uuid4().hex[:8]}"
            user = User.objects.create_user(username=username)
            Profile.objects.create(
                user=user,
                matricule=f"ANON_{uuid.uuid4().hex[:8]}",
                est_responsable=False
            )
            login(request, user)
            return redirect('dashboard:dashboard')

        elif user_type == 'responsable':
            matricule = request.POST.get('matricule', '').strip()
            if not matricule:
                return render(request, 'authentification/login.html', {
                    'error': 'Le matricule est requis pour les responsables'
                })

            try:
                profile = Profile.objects.get(matricule=matricule)
                if not profile.est_responsable:
                    return render(request, 'authentification/login.html', {
                        'error': 'Ce matricule n\'a pas les droits de responsable'
                    })

                login(request, profile.user)

                # ✅ REDIRECTION VERS LE DASHBOARD (et non plus /admin/)
                return redirect('dashboard:dashboard')

            except Profile.DoesNotExist:
                return render(request, 'authentification/login.html', {
                    'error': 'Matricule non trouvé'
                })

    return render(request, 'authentification/login.html')


def custom_logout(request):
    user = request.user
    if user.is_authenticated and user.username.startswith("anonymous_"):
        auth_logout(request)
        user.delete()  # ⚠️ suppression définitive
    else:
        auth_logout(request)
    return redirect('authentification:login')