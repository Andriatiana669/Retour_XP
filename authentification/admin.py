# authentification/admin.py (version complète et corrigée)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from .models import Profile
import uuid

# Formulaire personnalisé pour la création d'utilisateur
class CustomUserCreationForm(UserCreationForm):
    matricule = forms.CharField(
        max_length=50, 
        required=False,
        help_text="Laisser vide pour génération automatique"
    )
    est_responsable = forms.BooleanField(
        required=False,
        help_text="Cocher si c'est un responsable"
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

# Formulaire personnalisé pour la modification d'utilisateur
class CustomUserChangeForm(UserChangeForm):
    matricule = forms.CharField(
        max_length=50, 
        required=False,
        help_text="Modifiable - doit être unique"
    )
    est_responsable = forms.BooleanField(
        required=False,
        help_text="Cocher si c'est un responsable"
    )
    
    class Meta:
        model = User
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            try:
                self.fields['matricule'].initial = self.instance.profile.matricule
                self.fields['est_responsable'].initial = self.instance.profile.est_responsable
            except Profile.DoesNotExist:
                pass

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profil'
    extra = 0  # Pas de formulaire supplémentaire

class CustomUserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    inlines = (ProfileInline,)
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'first_name', 'last_name', 'matricule', 'est_responsable'),
        }),
    )
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'email', 'matricule', 'est_responsable')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    list_display = ['username', 'email', 'first_name', 'last_name', 'get_matricule', 'is_responsable', 'is_staff']
    list_filter = ['profile__est_responsable', 'is_staff', 'is_superuser', 'is_active']
    
    def get_matricule(self, obj):
        try:
            return obj.profile.matricule
        except Profile.DoesNotExist:
            return 'Aucun'
    get_matricule.short_description = 'Matricule'
    
    def is_responsable(self, obj):
        try:
            return obj.profile.est_responsable
        except Profile.DoesNotExist:
            return False
    is_responsable.boolean = True
    is_responsable.short_description = 'Responsable'
    
    def save_model(self, request, obj, form, change):
        # Sauvegarde l'utilisateur
        super().save_model(request, obj, form, change)
        
        # Gère le profil
        matricule = form.cleaned_data.get('matricule')
        est_responsable = form.cleaned_data.get('est_responsable')
        
        if not matricule:
            matricule = f"USER_{obj.id:04d}"
        
        profile, created = Profile.objects.get_or_create(
            user=obj,
            defaults={
                'matricule': matricule,
                'est_responsable': est_responsable or False
            }
        )
        
        if not created:
            # Met à jour le profil existant
            profile.matricule = matricule
            profile.est_responsable = est_responsable or False
            profile.save()

# Réenregistrer le UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Admin séparé pour Profile (optionnel, mais utile pour la gestion)
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'matricule', 'est_responsable']
    list_filter = ['est_responsable']
    search_fields = ['user__username', 'user__email', 'matricule']
    list_editable = ['matricule', 'est_responsable']  # Permet la modification rapide
    
    def has_add_permission(self, request):
        # Désactive l'ajout direct de profils (ils sont créés via User)
        return False