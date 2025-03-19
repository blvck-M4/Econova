from django.urls import path
from . import views

urlpatterns = [
    path('', views.members, name='members'),
    path('connexion', views.connexion, name='connexion'),
    path('rejoindre', views.rejoindre, name='rejoindre'),

    path('deconnexion', views.deconnexion, name='deconnexion'),
    path('supprimer', views.supprimer, name='supprimer'),
    path('questionnaire', views.questionnaire, name='questionnaire'),
    path('conditions', views.conditions, name='conditions'),
    path('tableau-bord/profil', views.profil, name='profil'),
    path('tableau-bord/chatbot', views.chatbot, name='chatbot'),
    path('tableau-bord/reponseBot', views.reponseBot, name='reponseBot'),
    path('tableau-bord/bourse', views.bourse, name='bourse'),
    path('tableau-bord/page-principale', views.page_principale, name='page-principale'),
    path('chart/', views.chart_view, name='revenue_dashboard'),
]