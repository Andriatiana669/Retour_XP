# marches/models.py
from django.db import models
from django.utils import timezone

# ------------------------------------------------------------------
# LISTES ADMINISTRABLES
# ------------------------------------------------------------------
class EtatAffaire(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    couleur = models.CharField(max_length=7, help_text="Code hexadécimal de la couleur")
    couleur_fond = models.CharField(max_length=7, help_text="Code hexadécimal de la couleur de fond")

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "État d'affaire"
        verbose_name_plural = "États d'affaires"

class NomMarche(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom

class Prestation(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom

class NomClient(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom

class Solution(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    demande_demarche = models.BooleanField(default=False, help_text="Cocher si une démarche doit être saisie")

    def __str__(self):
        return self.nom

# ------------------------------------------------------------------
# MARCHÉ GLOBAL
# ------------------------------------------------------------------
class MarcheGlobal(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    nombre_projet = models.IntegerField(default=0, editable=False)

    def save(self, *args, **kwargs):
        if self.pk:
            self.nombre_projet = self.marches_detailles.count()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom} ({self.nombre_projet} projets)"

    class Meta:
        verbose_name = "Marché global"
        verbose_name_plural = "Marchés globaux"

# ------------------------------------------------------------------
# MARCHÉ DÉTAILLÉ
# ------------------------------------------------------------------
class MarcheDetaille(models.Model):
    marche_global = models.ForeignKey(MarcheGlobal, on_delete=models.CASCADE, related_name='marches_detailles')
    matricule = models.CharField(max_length=50, unique=True, blank=True)
    resp_marche = models.ManyToManyField('authentification.Profile', related_name='marches_resp', blank=True)
    nom_marche = models.ForeignKey(NomMarche, on_delete=models.PROTECT)
    prestation = models.ManyToManyField(Prestation, related_name='marches_prestation')
    etat_affaire = models.ForeignKey(EtatAffaire, on_delete=models.SET_NULL, null=True, blank=True)
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    objet = models.CharField(max_length=200)
    nom_client = models.ManyToManyField(NomClient, related_name='marches_client', blank=True)
    date_retour = models.DateField(blank=True, null=True)
    date_maj = models.DateTimeField(auto_now=True)

    @property
    def prestation_list(self):
        return ", ".join([str(p) for p in self.prestation.all()[:3]])

    def save(self, *args, **kwargs):
        if not self.matricule:
            self.matricule = f"{self.resp_marche.matricule}_{MarcheDetaille.objects.filter(resp_marche=self.resp_marche).count() + 1}"
        super().save(*args, **kwargs)
        self.marche_global.save()  # met à jour le compteur

    def __str__(self):
        return f"{self.nom_marche} - {self.titre}"

    class Meta:
        verbose_name = "Marché détaillé"
        verbose_name_plural = "Marchés détaillés"
        ordering = ['-date_maj']

# ------------------------------------------------------------------
# CARTE
# ------------------------------------------------------------------
class Carte(models.Model):
    marche_detaille = models.ForeignKey(MarcheDetaille, on_delete=models.CASCADE, related_name='cartes')
    titre = models.CharField(max_length=200)
    objet = models.CharField(max_length=200, blank=True)
    contenu = models.TextField()
    image = models.ImageField(upload_to='cartes_images/', blank=True, null=True)
    nom_client = models.ForeignKey(NomClient, on_delete=models.PROTECT)
    date_retour = models.DateField()
    date_maj = models.DateTimeField(auto_now=True)

    solution = models.ForeignKey(Solution, on_delete=models.PROTECT)
    demarche_solution = models.TextField(blank=True, help_text="À remplir uniquement si la solution choisie l’exige")
    nom_dossier = models.CharField(max_length=200, blank=True, help_text="Nom du dossier associé")
    date_livraison = models.DateField(blank=True, null=True, help_text="À remplir uniquement si la solution choisie l’exige")

    def save(self, *args, **kwargs):
        # on efface la démarche si la solution ne la demande pas
        if self.solution and not self.solution.demande_demarche:
            self.demarche_solution = ""
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titre

    class Meta:
        verbose_name = 'Carte'
        verbose_name_plural = 'Cartes'