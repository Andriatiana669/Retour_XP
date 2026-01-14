# marches/models.py
from django.db import models
from django.utils import timezone

class EtatAffaire(models.Model):
    nom = models.CharField(max_length=50)
    couleur = models.CharField(max_length=7, help_text="Code hexadécimal de la couleur")
    couleur_fond = models.CharField(max_length=7, help_text="Code hexadécimal de la couleur de fond")
    
    def __str__(self):
        return self.nom
    
    class Meta:
        verbose_name = "État d'affaire"
        verbose_name_plural = "États d'affaires"

class MarcheGlobal(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    nombre_projet = models.IntegerField(default=0, editable=False) # Compteur de projets associés
    
    def save(self, *args, **kwargs):
        # Met à jour automatiquement le nombre de projets
        if self.pk:
            self.nombre_projet = self.marches_detailles.count()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.nom} ({self.nombre_projet} projets)"
    
    class Meta:
        verbose_name = "Marché global"
        verbose_name_plural = "Marchés globaux"

class MarcheDetaille(models.Model):
    marche_global = models.ForeignKey(MarcheGlobal, on_delete=models.CASCADE, related_name='marches_detailles')
    matricule = models.CharField(max_length=50, unique=False, blank=True)  # Rendu non obligatoire
    resp_marche = models.ForeignKey('authentification.Profile', on_delete=models.CASCADE)  # Changé en ForeignKey
    nom_marche = models.CharField(max_length=100)
    etat_affaire = models.ForeignKey(EtatAffaire, on_delete=models.SET_NULL, null=True, blank=True)
    # nombre_projet supprimé d'ici
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    objet = models.CharField(max_length=200)
    nom_client = models.CharField(max_length=100)
    date_retour = models.DateField(blank=True, null=True)
    date_maj = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Génère le matricule automatiquement si non défini
        if not self.matricule:
            self.matricule = self.resp_marche.matricule
        
        super().save(*args, **kwargs)
        
        # Met à jour le compteur du marché global
        self.marche_global.save()
    
    def __str__(self):
        return f"{self.nom_marche} - {self.titre}"
    
    class Meta:
        verbose_name = "Marché détaillé"
        verbose_name_plural = "Marchés détaillés"
        ordering = ['-date_maj']

class Carte(models.Model):
    marche_detaille = models.ForeignKey(MarcheDetaille, on_delete=models.CASCADE, related_name='cartes')
    titre      = models.CharField(max_length=200)
    objet      = models.CharField(max_length=200, blank=True)
    contenu    = models.TextField()
    image      = models.ImageField(upload_to='cartes_images/', blank=True, null=True)
    nom_client = models.CharField(max_length=100, blank=True)
    date_retour = models.DateField()                       # obligatoire
    date_maj   = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titre

    class Meta:
        verbose_name = 'Carte'
        verbose_name_plural = 'Cartes'