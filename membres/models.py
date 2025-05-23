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
    sexe = models.CharField(max_length=100, null=True)
    date_de_naissance = models.DateField(null=True)
    statut_professionnelle = models.CharField(max_length=255, null=True)
    revenu_mensuelle = models.CharField(max_length=255, null=True)
    statut_marital = models.CharField(max_length=255, null=True)
    parent = models.BooleanField(default=False)
    nombre_enfant = models.CharField(max_length=255, null=True)
    situation_habitation = models.CharField(max_length=255, null=True)


    # Types de dettes
    montant_dette = models.CharField(max_length=255, null=True)
    dette_credits = models.BooleanField(default=False)
    dette_pret_etudiant = models.BooleanField(default=False)
    dette_pret_automobile = models.BooleanField(default=False)
    dette_hypotheque = models.BooleanField(default=False)
    dette_autre = models.CharField(max_length=255, null=True)

    # Objectifs financiers
    acheter_maison =models.BooleanField(default=False)
    preparation_retraite = models.BooleanField(default=False)
    fond_urgence = models.BooleanField(default=False)
    rembourser_dettes = models.BooleanField(default=False)
    epargne_etudes = models.BooleanField(default=False)
    revenue_passif = models.BooleanField(default=False)
    independance_financier = models.BooleanField(default=False)
    investir = models.BooleanField(default=False)
    autre_objectif = models.CharField(max_length=255, null=True)

    tolerance_risque = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.utilisateur} - {self.prenom} {self.nom_de_famille}"

class RevenueMensuelle(models.Model):
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE)
    month = models.DateField()  # Store the month and year
    revenue = models.DecimalField(max_digits=10, decimal_places=2)  # Store revenue as a float or decimal

    def __str__(self):
        return f"{self.membre} - {self.month} - {self.revenue}"