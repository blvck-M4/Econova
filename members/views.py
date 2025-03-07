from django.contrib.auth import user_logged_in
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse
from django.template import loader
from .models import Member
conditions_termes = False
from dotenv import load_dotenv
load_dotenv()
import os
from google import genai
from google.genai import types
from django.http import JsonResponse


def reponseBot(request):
    if request.method == "POST":
        user_message = request.POST.get("message")
        client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY"),
        )

        model = "gemini-2.0-flash"
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=user_message),
                ],
            ),
        ]
        generate_content_config = types.GenerateContentConfig(
            temperature=1,
            top_p=0.95,
            top_k=64,
            max_output_tokens=8192,
            safety_settings=[
                types.SafetySetting(
                    category="HARM_CATEGORY_HARASSMENT",
                    threshold="BLOCK_ONLY_HIGH",  # Block few
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_HATE_SPEECH",
                    threshold="BLOCK_ONLY_HIGH",  # Block few
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    threshold="BLOCK_ONLY_HIGH",  # Block few
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold="BLOCK_ONLY_HIGH",  # Block few
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_CIVIC_INTEGRITY",
                    threshold="BLOCK_ONLY_HIGH",  # Block few
                ),
            ],
            response_mime_type="text/plain",
            system_instruction=[
                types.Part.from_text(text="""Tu es NOVA, un conseiller financier virtuel intelligent conçu pour 
                accompagner les utilisateurs d’EcoNova dans la gestion et l’optimisation de leurs finances personnelles. Propulsé par l’intelligence artificielle, NOVA analyse les habitudes financières des utilisateurs et leur propose des stratégies adaptées à leur profil et à leurs objectifs d’investissement."""),
            ],
        )
        reponse = ""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            reponse += chunk.text +" "
        return JsonResponse({"response": reponse})

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
            conditions_termes = True;
            return redirect('tableau-bord/profil')
        else:
            conditions_termes = False;
            return redirect('questionnaire')
    return HttpResponse(template.render(context, request))

def profil(request):
    urilisateurs = User.objects.all().values()
    members = Member.objects.all()
    context = {
        'urilisateurs': urilisateurs,
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
                    print(user.password)
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




