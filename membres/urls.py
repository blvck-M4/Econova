from django.urls import path
from . import views

urlpatterns = [
    path('', views.membres, name='membres'),
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
    path('tableau-bord/simulation', views.simulation, name='simulation'),
    path('education', views.education, name='education'),
    path('qstProfil', views.qstProfil, name='qstProfil'),
    path('tableau-bord/suivi', views.suivi, name='suivi'),
    path('tableau-bord/lancer_simulation', views.lancer_simulation, name='lancer_simulation'),
    path('tableau-bord/suivi/analyse', views.analyse, name='analyse'),
    path('tableau-bord/suivi/revenues', views.revenues, name='revenues'),
    path('tableau-bord/suivi/depenses', views.depenses, name='depenses'),

]