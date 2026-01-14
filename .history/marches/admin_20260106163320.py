# marches/admin.py
from django.contrib import admin
from django import forms
from .models import EtatAffaire, MarcheGlobal, MarcheDetaille, Carte
from authentification.models import Profile


# ------------------------------
# ÉTAT D’AFFAIRE
# ------------------------------
@admin.register(EtatAffaire)
class EtatAffaireAdmin(admin.ModelAdmin):
    list_display = ['nom', 'couleur', 'couleur_fond']
    list_editable = ['couleur', 'couleur_fond']


# ------------------------------
# MARCHÉ GLOBAL
# ------------------------------
@admin.register(MarcheGlobal)
class MarcheGlobalAdmin(admin.ModelAdmin):
    list_display = ['nom', 'description', 'nombre_projet']
    search_fields = ['nom']
    readonly_fields = ['nombre_projet']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # mise à jour auto des compteurs
        for marche in qs:
            marche.save()
        return qs


# ------------------------------
# MARCHÉ DÉTAILLÉ
# ------------------------------
class MarcheDetailleForm(forms.ModelForm):
    class Meta:
        model = MarcheDetaille
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        champs_a_masquer = {'nom_client','description', 'objet', 'titre', 'date_retour'}
        for fld in champs_a_masquer:
            if fld in self.fields:
                self.fields[fld].widget = forms.HiddenInput()


class CarteInline(admin.TabularInline):
    model   = Carte
    extra   = 1
    fields  = ('titre', 'objet', 'nom_client', 'date_retour', 'contenu', 'image')
    readonly_fields = ('date_maj',)


@admin.register(MarcheDetaille)
class MarcheDetailleAdmin(admin.ModelAdmin):
    form = MarcheDetailleForm

    list_display = ['matricule', 'nom_marche', 'resp_marche', 'etat_affaire', 'date_maj']
    list_filter  = ['etat_affaire', 'marche_global']
    search_fields = ['matricule', 'nom_marche']
    readonly_fields = ['date_maj']
    ordering = ['-date_maj']

    fieldsets = (
        (None, {
            'fields': ('marche_global', 'nom_marche', 'resp_marche', 'etat_affaire')
        }),
    )

    inlines = [CarteInline]


# ------------------------------
# CARTE
# ------------------------------
@admin.register(Carte)
class CarteAdmin(admin.ModelAdmin):
    list_display = ['titre', 'marche_detaille', 'objet', 'nom_client', 'date_retour', 'date_maj']
    list_filter  = ['date_retour', 'date_maj']
    search_fields = ['titre', 'objet', 'nom_client', 'contenu']
    date_hierarchy = 'date_retour'
    readonly_fields = ('date_maj',)