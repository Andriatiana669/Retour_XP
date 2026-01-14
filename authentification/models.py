# authentification/models.py
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    matricule = models.CharField(max_length=50, unique=True)
    est_responsable = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.matricule}"