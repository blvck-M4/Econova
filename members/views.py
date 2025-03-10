from django.contrib.auth import user_logged_in
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse
from django.template import loader
from .models import Member
import requests
from django.shortcuts import render
from django.conf import settings

conditions_termes = False;
def members(request):
    urilisateurs = User.objects.all().values()
    template = loader.get_template('home.html')
    context = {
        'urilisateurs': urilisateurs,
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
        if len(mot_de_passe) > 8:
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
        user = auth.authenticate(username=utilisateur, password=mot_de_passe)

        if user is not None:
            auth.login(request, user)
            return redirect('members')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect")
            return redirect('connexion')

    return render(request, 'connexion.html')

def deconnexion(request):
    auth.logout(request)
    return redirect('members')

def questionnaire(request):
    urilisateurs = User.objects.all().values()
    template = loader.get_template('questionnaire.html')
    context = {
        'urilisateurs': urilisateurs
    }
    global conditions_termes

    if request.method == 'POST':
        conditions = request.POST['conditions']
        if conditions == 'on':
            user = request.user
            member = Member(utilisateur=user)
            member.save()
            print(member)
            conditions_termes = True;
            return redirect('profil')
        else:
            conditions_termes = False;
            return redirect('questionnaire')
    return HttpResponse(template.render(context, request))

def profil(request):
    template = loader.get_template('profil.html')
    urilisateurs = User.objects.all().values()
    members = Member.objects.all()
    context = {
        'urilisateurs': urilisateurs,
        'members': members
    }

    return HttpResponse(template.render(context, request))





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

    return render(request, "bourse.html", {"stock_data": stock_data})
