from django.contrib.auth import user_logged_in
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse
from django.template import loader
from .models import Member
def members(request):
    urilisateurs = User.objects.all().values()
    template = loader.get_template('home.html')
    context = {
        'urilisateurs': urilisateurs
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
                    return redirect('members')

        else:
            messages.info(request, "Les deux mots de passe ne sont pas identiques")
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
