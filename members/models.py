from datetime import timezone

from django.db import models

# Create your models here.
class Member(models.Model):
    prenom = models.CharField(max_length=100, null=True)
    nom_de_famille = models.CharField(max_length=100, null=True)
    utilisateur = models.CharField(max_length=100, null=True)
    email = models.EmailField()
    mot_de_passe = models.CharField(max_length=100)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.prenom} {self.nom_de_famille}"