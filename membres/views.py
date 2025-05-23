import json
from collections import defaultdict
from datetime import datetime
from os import utime

from django.contrib.auth import user_logged_in
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse
from django.template import loader
from idna.uts46data import uts46data

from .models import Membre
from django.conf import settings
import requests
conditions_termes = False

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import nova_ai, bourse_data, simulation as nova_sim

# Affiche la page d'accueil avec la liste des utilisateurs
def membres(request):
    utilisateurs = User.objects.all().values()
    template = loader.get_template('home.html')
    context = {
        'utilisateurs': utilisateurs,
        'conditions_termes': conditions_termes,
    }
    return HttpResponse(template.render(context, request))

# Gère l'inscription d'un nouvel utilisateur (vérifie les champs, crée un User et un Membre)
def rejoindre(request):
    membres = Membre.objects.all().values()
    if request.method == 'POST':
        prenom = request.POST['prenom']
        nom_de_famille = request.POST['nom_de_famille']
        email = request.POST['email']
        utilisateur = request.POST['utilisateur']
        mot_de_passe = request.POST['mot_de_passe']
        mot_de_passe2 = request.POST['mot_de_passe2']
        if len(mot_de_passe) >= 8:
            if mot_de_passe == mot_de_passe2:
                if User.objects.filter(email=email).exists():
                    messages.info(request, 'Email déjà utilisé')
                    return redirect('rejoindre')
                elif User.objects.filter(username=utilisateur).exists():
                    messages.info(request, "Nom d'utilisateur déjà utilisé")
                    return redirect('rejoindre')
                else:
                    user = User.objects.create_user(username=utilisateur, password=mot_de_passe, email=email,
                                                    first_name=prenom, last_name=nom_de_famille)
                    user.save()
                    membre = Membre(utilisateur=utilisateur, prenom=prenom, nom_de_famille=nom_de_famille,
                                    email=email, mot_de_passe=mot_de_passe, date_creation=datetime.now())
                    membre.save()
                    if user is not None:
                        auth.login(request, user)
                        return redirect('questionnaire')

            else:
                messages.info(request, "Les deux mots de passe ne sont pas identiques")
                return redirect('rejoindre')
        else:
            messages.info(request, "Mot de passe trop court")
            return redirect('rejoindre')

    return render(request, 'rejoindre.html')

# Gère la connexion d'un utilisateur avec authentification
def connexion(request):
    if request.method == 'POST':
        utilisateur = request.POST['utilisateur']
        mot_de_passe = request.POST['mot_de_passe']
        for user in User.objects.all():
            print(user.username + ' ' + user.password)
        user = auth.authenticate(username=utilisateur, password=mot_de_passe)

        if user is not None:
            auth.login(request, user)
            global conditions_termes
            conditions_termes = True
            return redirect('tableau-bord/page-principale')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect")
            return redirect('connexion')

    return render(request, 'connexion.html')

# Gère le questionnaire rempli après l'inscription (met à jour les infos du Membre)
def questionnaire(request):
    membres = Membre.objects.all()
    utilisateurs = User.objects.all().values()
    template = loader.get_template('questionnaire.html')
    context = {'utilisateurs': utilisateurs}

    global conditions_termes

    if request.method == 'POST':

        date_naissance = request.POST.get('dateNaissance')
        statut_professionnelle = request.POST.get('situation')
        revenu_mensuelle = request.POST.get('revenu')
        statut_marital = request.POST.get('statut')
        conditions = request.POST.get('conditions')
        parent = request.POST.get('enfant')
        nombre_enfant = request.POST.get('nbEnfants')
        situation_habitation = request.POST.get('habitation')
        sexe = request.POST.get('sexe') #

        montant_dette = request.POST.get('montantDette')
        dette_credits = request.POST.get('detteCredit')
        dette_pret_etudiant = request.POST.get('detteEtudiant')
        dette_pret_automobile = request.POST.get('detteAutomobile')
        dette_hypotheque = request.POST.get('detteHypotheque')
        dette_autre = request.POST.get('AutreDette')

        acheter_maison = request.POST.get('acheterMaison')
        preparation_retraite = request.POST.get('preparationRetraite')
        fond_urgence = request.POST.get('fondUrgence')
        rembourser_dette = request.POST.get('rembourserDette')
        epargne_etudes = request.POST.get('epargneEtude')
        revenue_passif = request.POST.get('revenuePassif')
        independance_financier = request.POST.get('independanceFinanciere')
        investir = request.POST.get('investir')
        aucun = request.POST.get('aucun')
        autre_objectif = request.POST.get('autreObjectif')

        # Ensure date_naissance is a valid date object
        if date_naissance:
            date_naissance = datetime.strptime(date_naissance, "%Y-%m-%d").date()

        if sexe == "Autre":
            sexe = request.POST.get('autreSexe')

        # If "Autre" is selected for profession, get the custom value
        if statut_professionnelle == "Autre":
            statut_professionnelle = request.POST.get('autreSituation')

        if statut_marital == "Autre":
            statut_marital = request.POST.get('autreStatut')


        if situation_habitation == "Autre":
            situation_habitation = request.POST.get('autreHabitation')

        if autre_objectif == 'on':
            autre_objectif = request.POST.get('autreObjectifSpecifique')

        if dette_autre == 'on':
            dette_autre = request.POST.get('typeAutreDette')

        # Ensure conditions are accepted before updating
        if conditions == 'on':  # Check if the conditions box is checked
            user = request.user
            try:
                membre = membres.get(utilisateur=user.username)
            except Membre.DoesNotExist:
                membre = None  # Handle case where the user is not found in Membre

            if membre is not None:
                # Update fields
                membre.date_de_naissance = date_naissance
                membre.statut_professionnelle = statut_professionnelle
                membre.revenu_mensuelle = revenu_mensuelle
                membre.statut_marital = statut_marital
                membre.parent = (parent == 'Oui')  # Convert to boolean
                membre.sexe = sexe
                if membre.parent:  # Only set if parent is "Yes"
                    membre.nombre_enfant = nombre_enfant
                else:
                    membre.nombre_enfant = None  # Clear if not a parent


                membre.situation_habitation = situation_habitation
                membre.montant_dette = montant_dette
                membre.dette_credits = dette_credits == 'on'
                membre.dette_pret_etudiant = dette_pret_etudiant == 'on'
                membre.dette_pret_automobile = dette_pret_automobile == 'on'
                membre.dette_hypotheque = dette_hypotheque == 'on'
                membre.dette_autre = dette_autre

                membre.acheter_maison = acheter_maison =='on'
                membre.preparation_retraite = preparation_retraite =='on'
                membre.fond_urgence = fond_urgence == 'on'
                membre.rembourser_dettes = rembourser_dette == 'on'
                membre.epargne_etudes = epargne_etudes == 'on'
                membre.revenue_passif = revenue_passif == 'on'
                membre.independance_financier = independance_financier == 'on'
                membre.investir = investir == 'on'
                membre.aucun = aucun == 'on'
                membre.autre_objectif = autre_objectif


                membre.save()

                conditions_termes = True
                return redirect('tableau-bord/page-principale')
        else:
            conditions_termes = False
            return redirect('questionnaire')

    return HttpResponse(template.render(context, request))
# Affiche les conditions d'utilisation
def conditions(request):
    utilisateurs = User.objects.all().values()
    template = loader.get_template('conditions.html')
    context = {
        'utilisateurs': utilisateurs,
    }
    return HttpResponse(template.render(context, request))

# Affiche la page principale du tableau de bord
def page_principale(request):
    utilisateurs = User.objects.all()
    members = Membre.objects.all()
    context = {
        'utilisateurs': utilisateurs,
        'membres': members,
    }

    return render(request, 'tableau-bord/page-principale.html',context)

# Affiche et permet de modifier le profil de l'utilisateur
def profil(request):
    utilisateurs = User.objects.all().values()
    membres = Membre.objects.all()

    user = request.user
    try:
        membre = membres.get(utilisateur=user.username)
    except Membre.DoesNotExist:
        membre = None  # Handle case where the user is not found in Membre

    datenaissance = membre.date_de_naissance
    genre = membre.sexe
    if request.method == 'POST':
        user = request.user
        utilisateur = user.username
        for member in membres:
            if member.utilisateur == user.username:
                if request.POST['prenom'] != '' and request.POST['nom_de_famille'] != '':
                    user.first_name = request.POST['prenom']
                    user.last_name = request.POST['nom_de_famille']
                elif request.POST['email'] != '' and request.POST['email'] != user.email:
                    user.email = request.POST['email']
                elif request.POST['sexe'] != '' and request.POST['sexe'] != genre:
                    member.sexe = request.POST['sexe']
                elif request.POST['date_naissance'] != '' and request.POST['date_naissance'] != datenaissance:
                    member.date_de_naissance = request.POST['date_naissance']
                elif request.POST['utilisateur'] != '' and request.POST['utilisateur'] != user.username:
                    user.username = request.POST['utilisateur']
                    member.utilisateur = request.POST['utilisateur']
                elif request.POST['mot_de_passe'] != '' and request.POST['mot_de_passe'] != user.password:
                    nouveau_motdepasse = request.POST.get('mot_de_passe')
                    if nouveau_motdepasse:
                        user.set_password(nouveau_motdepasse)
                    user.save();
                    user = auth.authenticate(username=utilisateur, password=nouveau_motdepasse)

                    if user is not None:
                        auth.login(request, user)
                        return redirect('tableau-bord/profil')
                user.save()
                member.save()
                print(member.date_de_naissance)
        return redirect('profil')
    context = {
        'utilisateurs': utilisateurs,
        'membres': membres,
        'datenaissance': membre.date_de_naissance,
        'statut': membre.statut_marital,
        'genre': membre.sexe,

    }
    return render(request, 'tableau-bord/profil.html', context)

# Affiche la page du chatbot Nova dans le tableau de bord
def chatbot(request):
    utilisateurs = User.objects.all().values()
    context = {
        'utilisateurs': utilisateurs,
    }
    return render(request, 'tableau-bord/chatbot.html', context)

# Affiche la page de simulation et prépare les données pour les graphiques (actions, cryptos)
def simulation(request):
    utilisateurs = User.objects.all().values()
    liste_actions = nova_sim.listeProduits(nova_ai.listeProduits('actions'))
    liste_cryptos = nova_sim.listeProduits(nova_ai.listeProduits('cryptomonnaies'))
    graph_actions = []
    for action in liste_actions:
        liste_donnees = nova_sim.graphProduit(action)
        graph_actions.append({
            "nom": action['nom'],  # ou action.symbole si tu préfères
            "donnees": liste_donnees
        })
    graph_cryptos = []
    for crypto in liste_cryptos:
        liste_donnees = nova_sim.graphProduit(crypto)
        graph_cryptos.append({
            "nom": crypto['nom'],  # ou action.symbole si tu préfères
            "donnees": liste_donnees
        })

    context = {
        'utilisateurs': utilisateurs,
        'listeActions': liste_actions,
        'listeCryptos': liste_cryptos,
        'actionsGraph': graph_actions,
        'cryptosGraph': graph_cryptos,

    }
    return render(request, 'tableau-bord/simulation.html', context)

# Clé API Alpha Vantage (ajoute ta clé API dans settings.py)
ALPHA_VANTAGE_API_KEY = settings.ALPHA_VANTAGE_API_KEY
# Affiche la page bourse avec les données récupérées depuis l'API
def bourse(request):
    utilisateurs = User.objects.all().values()
    membre = Membre.objects.all()
    stock_data = bourse_data.stock_data(request)

    context = {
        'utilisateurs': utilisateurs,
        'membres': membre,
        "stock_data": stock_data,
    }
    return render(request, "tableau-bord/bourse.html", context)



# Affiche la page d’éducation financière
def education(request):
    utilisateurs = User.objects.all().values()
    context = {
        'utilisateurs': utilisateurs,
    }
    return render(request, 'education.html', context)

# Affiche la page de suivi général dans le tableau de bord
def suivi(request):
    utilisateurs = User.objects.all().values()
    members = Membre.objects.all()
    context = {
        'utilisateurs': utilisateurs,
        'members': members,
    }
    return render(request, 'tableau-bord/suivi/suivi.html', context)
# Affiche la sous-page d’analyse dans la section Suivi
def analyse(request):
    return render(request, 'tableau-bord/suivi/analyse.html')
# Affiche la sous-page de revenus dans la section Suivi
def revenues(request):
    return render(request, 'tableau-bord/suivi/revenues.html')
# Affiche la sous-page de dépenses dans la section Suivi
def depenses(request):
    return render(request, 'tableau-bord/suivi/depenses.html')

#Fonctionnalités

# Déconnecte l'utilisateur
def deconnexion(request):
    auth.logout(request)
    return redirect('membres')

# Supprime le compte et les données du Membre associé
def supprimer(request):
    membres = Membre.objects.all()
    for membre in membres:
        if membre.utilisateur == request.user.username:
            membre.delete()
    auth.get_user(request).delete()
    return redirect('membres')

# Reçoit un message utilisateur et retourne une réponse du chatbot Nova
@csrf_exempt
def reponseBot(request):
    if request.user.is_authenticated:
        user = request.user
        utilisateur = user.username
    else:
        utilisateur = "anonyme"

    print('Utilisateur 1: '+utilisateur)

    reponse = nova_ai.reponseBot(request, utilisateur)
    return JsonResponse({"response": reponse})

# Fournit des questions de profil personnalisées pour Nova
@csrf_exempt
def qstProfil(request):
    if user_logged_in:
        user = request.user
        utilisateur = user.username
    else:
        utilisateur = 'anonyme'
    print(utilisateur)
    reponse = nova_ai.qstProfil(request, utilisateur)
    return JsonResponse({"response": reponse})

# Lance la simulation Monte Carlo pour un symbole et un nombre d'années donné
@csrf_exempt
def lancer_simulation(request):
    if request.method == "POST":
        symbole = request.POST.get('message').split(' - ')[0]
        nbannees = int(request.POST.get('message').split(' - ')[1])

        # Simulation qui retourne un tableau numpy
        simulations = nova_sim.lancerSimulations(symbole, nbannees)

    return JsonResponse({"response": simulations})