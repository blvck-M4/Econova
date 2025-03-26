from django.contrib import admin
from .models import Membre
# Register your models here.

class MemberAdmin(admin.ModelAdmin):
    list_display = ("utilisateur","prenom", "nom_de_famille", "date_creation")

admin.site.register(Membre, MemberAdmin)