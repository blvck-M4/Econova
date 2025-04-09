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

from .forms import RevenueMensuelleForms
from .models import Membre, RevenueMensuelle
from django.conf import settings
import requests

from .models import Membre

conditions_termes = False

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import nova_ai, bourse_data

def membres(request):
    utilisateurs = User.objects.all().values()
    template = loader.get_template('home.html')
    context = {
        'utilisateurs': utilisateurs,
        'conditions_termes': conditions_termes,
    }
    return HttpResponse(template.render(context, request))


def rejoindre(request):
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
        sexe = request.POST.get('sexe')

        montant_dette = request.POST.get('montantDette')
        dette_credits = request.POST.get('detteCredit')
        dette_pret_etudiant = request.POST.get('detteEtudiant')
        dette_pret_automobile = request.POST.get('detteAutomobile')
        dette_hypotheque = request.POST.get('detteHypotheque')
        dette_autre = request.POST.get('AutreTypeDette')

        acheter_maison = request.POST.get('acheterMaison')
        preparation_retraite = request.POST.get('preparationRetraite')
        fond_urgence = request.POST.get('fondUrgence')
        rembourser_dette = request.POST.get('rembourserDette')
        epargne_etudes = request.POST.get('epargneEtude')
        revenue_passif = request.POST.get('revenuePassif')
        independance_financiere = request.POST.get('independanceFinanciere')
        investir = request.POST.get('investir')
        aucun = request.POST.get('aucun')
        autre_objectif = request.POST.get('autreObjectif')

        # Ensure date_naissance is a valid date object
        if date_naissance:
            date_naissance = datetime.strptime(date_naissance, "%Y-%m-%d").date()

        # If "Autre" is selected for profession, get the custom value
        if statut_professionnelle == "Autre":
            statut_professionnelle = request.POST.get('autre_situation', 'Autre')  # Get the text if Autre is selected

        if autre_objectif == "Autre":
            statut_professionnelle = request.POST.get('autre_situation', 'Autre')

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
                membre.dette_credits = dette_credits =='on'
                membre.dette_pret_etudiant = dette_pret_etudiant == 'on'
                membre.dette_pret_automobile = dette_pret_automobile == 'on'
                membre.dette_hypotheque = dette_hypotheque == 'on'
                membre.dette_autre = dette_autre =='on'

                membre.acheter_maison = acheter_maison =='on'
                membre.preparation_retraite = preparation_retraite =='on'
                membre.fond_urgence = fond_urgence =='on'
                membre.rembourser_dette = rembourser_dette == 'on'
                membre.epargne_etudes = epargne_etudes == 'on'
                membre.revenue_passif = revenue_passif == 'on'
                membre.independance_financiere = independance_financiere == 'on'
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

def conditions(request):
    utilisateurs = User.objects.all().values()
    template = loader.get_template('conditions.html')
    context = {
        'utilisateurs': utilisateurs,
    }
    return HttpResponse(template.render(context, request))

#Pages du Tableau de bord
def page_principale(request):
    utilisateurs = User.objects.all()
    members = Membre.objects.all()
    context = {
        'utilisateurs': utilisateurs,
        'membres': members,
    }

    return render(request, 'tableau-bord/page-principale.html',context)


def profil(request):
    utilisateurs = User.objects.all().values()
    members = Membre.objects.all()
    context = {
        'utilisateurs': utilisateurs,
        'membres': members
    }

    if request.method == 'POST':
        user = request.user
        utilisateur = user.username
        for member in members:
            if member.utilisateur == user.username:
                if request.POST['prenom'] != '' and request.POST['nom_de_famille'] != '':
                    user.first_name = request.POST['prenom']
                    user.last_name = request.POST['nom_de_famille']
                elif request.POST['email'] != '' and request.POST['email'] != user.email:
                    user.email = request.POST['email']
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
        return redirect('profil')

    return render(request, 'tableau-bord/profil.html', context)

def chatbot(request):
    utilisateurs = User.objects.all().values()
    context = {
        'utilisateurs': utilisateurs,
    }
    return render(request, 'tableau-bord/chatbot.html', context)
def simulation(request):
    utilisateurs = User.objects.all().values()
    context = {
        'utilisateurs': utilisateurs,
    }
    return render(request, 'tableau-bord/simulation.html', context)

# Clé API Alpha Vantage (ajoute ta clé API dans settings.py)
ALPHA_VANTAGE_API_KEY = settings.ALPHA_VANTAGE_API_KEY
def bourse(request):
    utilisateurs = User.objects.all().values()
    membre = Membre.objects.all()
    stock_data = bourse_data.stock_data(request)
    conseil = nova_ai.conseilActions(stock_data, 'conservateur')
    print(conseil)

    context = {
        'utilisateurs': utilisateurs,
        'membres': membre,
        "stock_data": stock_data,
        'conseil': conseil,
    }
    return render(request, "tableau-bord/bourse.html", context)


#Fonctionnalités
def deconnexion(request):
    auth.logout(request)
    return redirect('membres')
def supprimer(request):
    membres = Membre.objects.all()
    for membre in membres:
        if membre.utilisateur == request.user.username:
            membre.delete()
    auth.get_user(request).delete()
    return redirect('membres')

@csrf_exempt
def reponseBot(request):
    if user_logged_in:
        user = request.user
        utilisateur = user.username
    else:
        utilisateur = 'anonyme'

    reponse = nova_ai.reponseBot(request, utilisateur)
    return JsonResponse({"response": reponse})

def chart_view(request):
    # Récupérer l'instance du membre correspondant en utilisant le nom d'utilisateur.
    try:
        membre = Membre.objects.get(utilisateur=request.user.username)
    except Membre.DoesNotExist:
        membre = None

    context = {}  # Assurez-vous que le contexte est toujours défini.

    # Vérifier si l'utilisateur veut effacer les revenus
    if request.method == "GET" and request.GET.get("clear_revenue") == "true" and membre is not None:
        RevenueMensuelle.objects.filter(membre=membre).delete()
        return redirect('suivi-financier')  # Redirection pour rafraîchir la page

    if request.method == "POST":
        form = RevenueMensuelleForms(request.POST)
        if form.is_valid() and membre is not None:
            # Extraire les données nettoyées
            mois = form.cleaned_data['month']
            revenue = form.cleaned_data['revenue']

            # Mettre à jour ou créer l'enregistrement MonthlyRevenue pour le mois et le membre donnés.
            RevenueMensuelle.objects.update_or_create(
                membre=membre,
                month=mois,
                defaults={'revenue': revenue}
            )
            # Rediriger pour éviter la resoumission lors du rafraîchissement.
            return redirect('suivi-financier')
        else:
            # Si le formulaire n'est pas valide, passez le formulaire au contexte.
            context['form'] = form
    else:
        form = RevenueMensuelleForms()
        context['form'] = form

    # Filtrer les entrées de revenus pour le membre actuel (si elles existent)
    revenue_ajouter = RevenueMensuelle.objects.filter(membre=membre) if membre else []

    # Agréger les revenus par mois
    revenue_par_mois = defaultdict(float)
    for ajout in revenue_ajouter:
        mois_str = ajout.month.strftime('%Y-%m')
        revenue_par_mois[mois_str] += float(ajout.revenue)

    sorted_months = sorted(revenue_par_mois.keys())
    # If there are no revenue entries, ensure we have at least one entry with 0 value
    if not revenue_par_mois:
        revenue_par_mois['No Data'] = 0  # Adding a default label and value for empty data
    mois_trier = sorted(revenue_par_mois.keys())
    labels = mois_trier
    values = [revenue_par_mois[month] for month in mois_trier]

    chart_data = {
        "labels": labels,
        "values": values,
    }

    context['chart_data'] = json.dumps(chart_data)  # Toujours définir context['chart_data']
    return render(request, 'suivi-financier.html', context)