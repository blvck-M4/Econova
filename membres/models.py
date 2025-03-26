from django.db import models

# Create your models here.
class Membre(models.Model):
    # Informations générales
    prenom = models.CharField(max_length=100, null=True)
    nom_de_famille = models.CharField(max_length=100, null=True)
    utilisateur = models.CharField(max_length=100, unique=True, default="Unknown")  # Added unique constraint
    email = models.EmailField()
    mot_de_passe = models.CharField(max_length=100)
    date_creation = models.DateTimeField(auto_now_add=True)

    # Informations personnelles
    date_de_naissance = models.CharField(max_length=255, null=True, blank=True)
    statut_professionnelle = models.CharField(max_length=255, null=True, blank=True)
    revenu_mensuelle = models.CharField(max_length=255, null=True, blank=True)
    statut_marital = models.CharField(max_length=255, null=True, blank=True)
    parent = models.BooleanField(default=False)
    nombre_enfant = models.CharField(max_length=255, null=True, blank=True)
    situation_habitation = models.CharField(max_length=255, null=True, blank=True)
    objectifs_principales = models.CharField(max_length=255, null=True, blank=True)

    # Types de dettes
    dette_credits = models.BooleanField(default=False)
    dette_pret_etudiant = models.BooleanField(default=False)
    dette_pret_automobile = models.BooleanField(default=False)
    dette_hypotheque = models.BooleanField(default=False)
    dette_autre = models.BooleanField(default=False)

    tolerance_risque = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.utilisateur} - {self.prenom} {self.nom_de_famille}"  # Used 'utilisateur' instead of 'username'

class RevenueMensuelle(models.Model):
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE)
    month = models.DateField()  # Store the month and year
    revenue = models.DecimalField(max_digits=10, decimal_places=2)  # Store revenue as a float or decimal

    def __str__(self):
        return f"{self.membre} - {self.month} - {self.revenue}"