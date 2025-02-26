from django.urls import path
from . import views

urlpatterns = [
    path('members/', views.members, name='members'),
    path('members/connexion', views.connexion, name='connexion'),
    path('members/rejoindre', views.rejoindre, name='rejoindre'),

    path('members/deconnexion', views.deconnexion, name='deconnexion'),

]