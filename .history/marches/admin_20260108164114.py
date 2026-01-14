# marches/admin.py
from django.contrib import admin
from django import forms
from django.db import models
from .models import (
    EtatAffaire, NomMarche, Prestation, NomClient, Solution,
    MarcheGlobal, MarcheDetaille, Carte
)
from authentification.models import Profile

# ------------------------------------------------------------------
# LISTES ADMINISTRABLES
# ------------------------------------------------------------------
@admin.register(EtatAffaire)
class EtatAffaireAdmin(admin.ModelAdmin):
    list_display = ('nom', 'couleur', 'couleur_fond')
    list_editable = ('couleur', 'couleur_fond')
    search_fields = ('nom',)

@admin.register(NomMarche)
class NomMarcheAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)

@admin.register(Prestation)
class PrestationAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)

@admin.register(NomClient)
class NomClientAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)

@admin.register(Solution)
class SolutionAdmin(admin.ModelAdmin):
    list_display = ('nom', 'demande_demarche')
    list_editable = ('demande_demarche',)
    search_fields = ('nom',)

# ------------------------------------------------------------------
# MARCHÉ GLOBAL
# ------------------------------------------------------------------
@admin.register(MarcheGlobal)
class MarcheGlobalAdmin(admin.ModelAdmin):
    list_display = ('nom', 'nombre_projet')
    search_fields = ('nom',)
    readonly_fields = ('nombre_projet',)

# ------------------------------------------------------------------
# MARCHÉ DÉTAILLÉ
# ------------------------------------------------------------------
class CarteInline(admin.TabularInline):
    model = Carte
    extra = 1
    fields = ('titre', 'objet', 'nom_client', 'date_retour', 'contenu', 'image')
    readonly_fields = ('date_maj',)

class MarcheDetailleForm(forms.ModelForm):
    class Meta:
        model = MarcheDetaille
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # on masque les champs non utilisés (ils seront remplis via listes)
        for fld in ('description', 'objet', 'titre', 'date_retour'):
            if fld in self.fields:
                self.fields[fld].widget = forms.HiddenInput()

@admin.register(MarcheDetaille)
class MarcheDetailleAdmin(admin.ModelAdmin):
    form = MarcheDetailleForm

    list_display = ('matricule', 'nom_marche', 'prestation', 'nom_client', 'resp_marche', 'etat_affaire', 'date_maj')
    list_filter = ('etat_affaire', 'marche_global', 'nom_marche', 'prestation', 'nom_client')
    search_fields = ('matricule', 'titre', 'nom_marche__nom', 'prestation__nom', 'nom_client__nom')
    readonly_fields = ('date_maj',)
    ordering = ('-date_maj',)

    fieldsets = (
        (None, {
            'fields': ('marche_global', 'nom_marche', 'prestation', 'resp_marche', 'etat_affaire')
        }),
        ('Contenu administrable', {
            'fields': ('titre', 'objet', 'description', 'nom_client', 'date_retour')
        }),
    )

    inlines = [CarteInline]

# ------------------------------------------------------------------
# CARTE
# ------------------------------------------------------------------
class CarteForm(forms.ModelForm):
    class Meta:
        model = Carte
        fields = '__all__'

    def clean(self):
        cleaned = super().clean()
        solution = cleaned.get('solution')
        demarche = cleaned.get('demarche_solution')
        if solution and not solution.demande_demarche and demarche:
            cleaned['demarche_solution'] = ''  # on vide si pas demandé
        return cleaned

@admin.register(Carte)
class CarteAdmin(admin.ModelAdmin):
    form = CarteForm

    list_display = ('titre', 'marche_detaille', 'nom_client', 'solution', 'date_retour', 'date_maj')
    list_filter = ('solution', 'nom_client', 'date_retour', 'date_maj')
    search_fields = ('titre', 'objet', 'nom_client__nom', 'contenu')
    date_hierarchy = 'date_retour'
    readonly_fields = ('date_maj',)

    fieldsets = (
        (None, {
            'fields': ('marche_detaille', 'titre', 'objet', 'contenu', 'image', 'nom_client', 'date_retour')
        }),
        ('Solution & dossier', {
            'fields': ('solution', 'demarche_solution', 'nom_dossier'),
            'description': 'La démarche sera vide si la solution choisie ne l’exige pas.'
        }),
    )