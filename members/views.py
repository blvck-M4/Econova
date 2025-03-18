from os import utime

from django.contrib.auth import user_logged_in
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse
from django.template import loader
from .models import Member
from django.conf import settings
import requests
conditions_termes = False

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import nova_ai

@csrf_exempt
def reponseBot(request):
    if user_logged_in:
        user = request.user
        utilisateur = user.username
    else:
        utilisateur = 'anonyme'

    reponse = nova_ai.reponseBot(request, utilisateur)
    return JsonResponse({"response": reponse})

def members(request):
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
                    user = User.objects.create_user(username=utilisateur, password=mot_de_passe, email=email, first_name=prenom, last_name=nom_de_famille)
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
            print(user.username +' '+user.password)
        user = auth.authenticate(username=utilisateur, password=mot_de_passe)

        if user is not None:
            auth.login(request, user)
            global conditions_termes
            conditions_termes = True
            return redirect('tableau-bord/profil')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect")
            return redirect('connexion')

    return render(request, 'connexion.html')

def deconnexion(request):
    auth.logout(request)
    return redirect('members')
def supprimer(request):
    members = Member.objects.all()
    for member in members:
        if member.utilisateur == request.user.username:
            member.delete()
    auth.get_user(request).delete()
    return redirect('members')

def questionnaire(request):
    utilisateurs = User.objects.all().values()
    template = loader.get_template('questionnaire.html')
    context = {
        'utilisateurs': utilisateurs
    }
    global conditions_termes
    if request.method == 'POST':
        conditions = request.POST['conditions']
        if conditions == 'on':
            user = request.user
            member = Member(utilisateur=user)
            member.save()
            conditions_termes = True;
            return redirect('tableau-bord/profil')
        else:
            conditions_termes = False;
            return redirect('questionnaire')
    return HttpResponse(template.render(context, request))

def profil(request):
    utilisateurs = User.objects.all().values()
    members = Member.objects.all()
    context = {
        'utilisateurs': utilisateurs,
        'members': members
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
    urilisateurs = User.objects.all().values()
    context = {
        'urilisateurs': urilisateurs,
    }
    return render(request, 'tableau-bord/chatbot.html', context)

# Clé API Alpha Vantage (ajoute ta clé API dans settings.py)
ALPHA_VANTAGE_API_KEY = settings.ALPHA_VANTAGE_API_KEY
def bourse(request):
    stock_data = None  # Par défaut, pas de données

    if 'symbol' in request.GET:
        symbol = request.GET['symbol'].upper()

        # Récupération des données depuis Alpha Vantage
        url = f"https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": ALPHA_VANTAGE_API_KEY,
            "outputsize": "compact"
        }

        response = requests.get(url, params=params)
        data = response.json()

        if "Time Series (Daily)" in data:
            time_series = data["Time Series (Daily)"]
            dates = list(time_series.keys())[:30]  # Récupère les 30 derniers jours
            prices = [float(time_series[date]["4. close"]) for date in dates]

            stock_data = {
                "symbol": symbol,
                "name": symbol,  # Alpha Vantage n'a pas de champ 'nom', mais tu peux le compléter
                "last_price": prices[0],  # Dernier prix
                "change": round(prices[0] - prices[1], 2),
                "percent_change": round(((prices[0] - prices[1]) / prices[1]) * 100, 2),
                "dates": dates[::-1],  # Inverser pour afficher dans le bon ordre
                "prices": prices[::-1]
            }

    return render(request, "tableau-bord/bourse.html", {"stock_data": stock_data})


