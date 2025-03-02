from django.urls import path
from . import views

urlpatterns = [
    path('', views.members, name='members'),
    path('connexion', views.connexion, name='connexion'),
    path('rejoindre', views.rejoindre, name='rejoindre'),

    path('deconnexion', views.deconnexion, name='deconnexion'),
    path('questionnaire', views.questionnaire, name='questionnaire'),
    path('profil', views.profil, name='profil'),

]