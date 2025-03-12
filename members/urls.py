from django.urls import path
from . import views

urlpatterns = [
    path('', views.members, name='members'),
    path('connexion', views.connexion, name='connexion'),
    path('rejoindre', views.rejoindre, name='rejoindre'),

    path('deconnexion', views.deconnexion, name='deconnexion'),
    path('supprimer', views.supprimer, name='supprimer'),
    path('questionnaire', views.questionnaire, name='questionnaire'),
    path('tableau-bord/profil', views.profil, name='profil'),
    path('tableau-bord/chatbot', views.chatbot, name='chatbot'),
    path('tableau-bord/reponseBot', views.reponseBot, name='reponseBot'),
    path('tableau-bord/bourse', views.bourse, name='bourse'),

]