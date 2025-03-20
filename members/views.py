import json
from collections import defaultdict
from os import utime

from django.contrib.auth import user_logged_in
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse
from django.template import loader

from .forms import MonthlyRevenueForm
from .models import Member, MonthlyRevenue
from django.conf import settings
import requests

from .models import Member

conditions_termes = False

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import nova_ai, bourse_data

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

def questionnaire(request):
    members = Member.objects.all()
    utilisateurs = User.objects.all().values()
    template = loader.get_template('questionnaire.html')
    context = {
        'utilisateurs': utilisateurs
    }
    global conditions_termes
    if request.method == 'POST':
        date_naissance = request.POST['date_naissance']
        conditions = request.POST['conditions']
        if conditions == 'on':
            user = request.user
            member = members.filter(utilisateur=user.username)
            if member is not None:
                member.date_naissance = date_naissance
            member.save()
            conditions_termes = True;
            return redirect('tableau-bord/profil')
        else:
            conditions_termes = False;
            return redirect('questionnaire')
    return HttpResponse(template.render(context, request))

def conditions(request):
    urilisateurs = User.objects.all().values()
    template = loader.get_template('conditions.html')
    context = {
        'urilisateurs': urilisateurs,
    }
    return HttpResponse(template.render(context, request))

#Pages du Tableau de bord
def page_principale(request):
    utilisateurs = User.objects.all()
    members = Member.objects.all()
    context = {
        'utilisateurs': utilisateurs,
        'members': members,
    }

    return render(request, 'tableau-bord/page-principale.html',context)


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
    utilisateurs = User.objects.all().values()
    context = {
        'utilisateurs': utilisateurs,
    }
    return render(request, 'tableau-bord/chatbot.html', context)

# Clé API Alpha Vantage (ajoute ta clé API dans settings.py)
ALPHA_VANTAGE_API_KEY = settings.ALPHA_VANTAGE_API_KEY
def bourse(request):
    urilisateurs = User.objects.all().values()
    members = Member.objects.all()
    stock_data = bourse_data.stock_data(request)
    conseil = nova_ai.conseilActions(stock_data, 'conservateur')
    print(conseil)

    context = {
        'urilisateurs': urilisateurs,
        'members': members,
        "stock_data": stock_data,
        'conseil': conseil,
    }
    return render(request, "tableau-bord/bourse.html", context)


#Fonctionnalités
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
        member = Member.objects.get(utilisateur=request.user.username)
    except Member.DoesNotExist:
        member = None

    context = {}  # Assurez-vous que le contexte est toujours défini.

    # Vérifier si l'utilisateur veut effacer les revenus
    if request.method == "GET" and request.GET.get("clear_revenue") == "true" and member is not None:
        MonthlyRevenue.objects.filter(member=member).delete()
        return redirect('revenue_dashboard')  # Redirection pour rafraîchir la page

    if request.method == "POST":
        form = MonthlyRevenueForm(request.POST)
        if form.is_valid() and member is not None:
            # Extraire les données nettoyées
            month = form.cleaned_data['month']
            revenue = form.cleaned_data['revenue']

            # Mettre à jour ou créer l'enregistrement MonthlyRevenue pour le mois et le membre donnés.
            MonthlyRevenue.objects.update_or_create(
                member=member,
                month=month,
                defaults={'revenue': revenue}
            )
            return redirect('revenue_dashboard')  # Rediriger pour éviter la resoumission
        else:
            context['form'] = form  # Si le formulaire n'est pas valide

    else:
        form = MonthlyRevenueForm()
        context['form'] = form

    # Filtrer les entrées de revenus pour le membre actuel (si elles existent)
    revenue_entries = MonthlyRevenue.objects.filter(member=member) if member else []

    # Agréger les revenus par mois
    revenue_by_month = defaultdict(float)
    for entry in revenue_entries:
        month_str = entry.month.strftime('%Y-%m')
        revenue_by_month[month_str] += float(entry.revenue)

    # If there are no revenue entries, ensure we have at least one entry with 0 value
    if not revenue_by_month:
        revenue_by_month['No Data'] = 0  # Adding a default label and value for empty data
    sorted_months = sorted(revenue_by_month.keys())
    labels = sorted_months
    values = [revenue_by_month[month] for month in sorted_months]

    chart_data = {
        "labels": labels,
        "values": values,
    }

    context['chart_data'] = json.dumps(chart_data)  # Toujours définir context['chart_data']

    return render(request, 'chart.html', context)