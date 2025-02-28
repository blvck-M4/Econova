from django.contrib.auth import user_logged_in
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse
from django.template import loader
from .models import Member

conditions_termes = False;
def members(request):
    urilisateurs = User.objects.all().values()
    member = Member.objects.all().values()
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
            return redirect('members')
        else:
            conditions_termes = False;
            return redirect('questionnaire')
    return HttpResponse(template.render(context, request))