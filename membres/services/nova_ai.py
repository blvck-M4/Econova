#Code de l'intelligence artificielle utilisée dans le site internet
import json

from django.conf import settings
from dotenv import load_dotenv

load_dotenv()
import os
import re

from google import genai
from google.genai import types

from membres.models import Membre
#Code récupérer de google ai studio (https://aistudio.google.com/app/prompts/new_chat) et modifié selon nos besoins
client = genai.Client(
    api_key=settings.GEMINI_API_KEY,
)
model = "gemini-2.0-flash"
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
)

#Génère la réponse du bot (Nova) lorsqu'il est questionné
def reponseBot(request, utilisateur):
    historique = request.session.get('historique', [])
    utilisateur_infos = ''
    print('Utilisateur: '+utilisateur)
    if utilisateur != 'anonyme':
        membre = Membre.objects.get(utilisateur=utilisateur)
        fields = membre._meta.get_fields()
        membre_str = ""

        for field in fields:
            if hasattr(membre, field.name):
                value = getattr(membre, field.name)
                membre_str += f"{field.name}: {value}, "
        utilisateur_infos = membre_str.rstrip(', ')


    if request.method == "POST":
        user_message = request.POST.get("message")
        historique.append({"role": "user", "text": user_message})
        # code google ai studio (modifié)
        contents = [
            types.Content(role=message["role"] if message["role"] == "user" else "model", parts=[types.Part.from_text(
                text=message["text"])])
            for message in historique

        ]
        # code google ai studio (modifié)
        generate_content_config.system_instruction = [
            types.Part.from_text(text="""Tu es NOVA, un conseiller financier virtuel intelligent conçu pour 
                                accompagner """ + utilisateur + """, un utilisateur d’EcoNova dans la gestion et l’optimisation de ses 
                                finances personnelles. Voici ses informations: """ + utilisateur_infos + """. 
                                Propulsé par l’intelligence artificielle, NOVA analyse les habitudes financières des utilisateurs et 
                                leur propose des stratégies adaptées à leur profil et à leurs objectifs d’investissement. Ne donne 
                                pas des réponses trop longues (plus de 500 mots) à part si c'est nécessaire. Quand une 
                                question ne fait pas de sens répond avec de l'humour. Répond avec des points numérotés quand c'est 
                                nécessaire et laisse des lignes entre différent point."""),
        ]
        reponse = ""
        # code google ai studio
        for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
        ):
            reponse += chunk.text
        reponse_filtre = reponse.replace('**', '<br>')
        reponse_finale = reponse_filtre.replace('*', ' ')

        historique.append({"role": "model", "text": reponse})
        request.session['historique'] = historique

        return reponse_finale



#Génère une liste de produits financier
liste_actions = []
liste_cryptos = []
def listeProduits(produit):
    if produit == 'actions':
        format = 'AAPL'
    elif produit == 'cryptomonnaies':
        format = 'BTC-CAD'
    else:
        format = ''

    # code google ai studio (modifié)
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""Génère le symbol de 10 """+produit+""" aléatoires du top 100 
                sous la 
                forme {
                """+format+""",
                ...}"""),
            ],
        ),

    ]
    # code google ai studio (modifié)
    generate_content_config.system_instruction = [
        types.Part.from_text(text="""Tu es un générateur de liste de """+produit+""" en français. Tu n'écris rien 
        d'autre que la 
        liste. Sépare la liste par une virgule sans 
            utilisé rien d'autre pour que je puisse réutiliser la liste facilement."""),
    ]
    reponse = ""
    if produit == 'actions':
        global liste_actions
        liste_produits = liste_actions
    elif produit == 'cryptomonnaies':
        global liste_cryptos
        liste_produits = liste_cryptos
    else:
        liste_produits = []
    if len(liste_produits) == 0:
        # code google ai studio
        for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
        ):
            reponse += chunk.text
        liste_produits = [produit.strip() for produit in reponse.split(',')]



    print(liste_produits)
    return liste_produits








#Programmation de l'IA du questionnaire de profil d'investisseur dans la section EDUCATION
def qstProfil(request, utilisateur):
    historique = request.session.get('historique2', [])

    if request.method == "POST":
        user_message = request.POST.get("message")
        historique.append({"role": "user", "text": user_message})

        # code google ai studio (modifié)
        contents = [
            types.Content(role=message["role"] if message["role"] == "user" else "model",
                          parts=[types.Part.from_text(text=message["text"])])
            for message in historique
        ]

        # code google ai studio (modifié)
        generate_content_config.system_instruction = [
            types.Part.from_text(text="""Tu es Nova un conseiller financier virtuel conçu pour aider""" + utilisateur + """
            du site ECONOVA à déterminer leur profil d’investisseur à travers 10 questions basées sur des mises en situation 
            que tu génères. Une question automatique sera posée à """ + utilisateur + """ avant que tu commences le questionnaire
            pour savoir si il est prêt pour s’assurer que tout est bien compris, tu prends la réponse de validation (oui/non)
            avant de commencer. Si c'est non demande quel est le problème, sinon commence le questionnaire. Chaque question 
            propose 3 à 4 choix de réponses clairs et concis. Tu détectes les incohérences logiques entre les réponses et invites
             """ + utilisateur + """ à corriger si nécessaire. L’humour est utilisé uniquement dans les réponses, lorsqu’une
            erreur ou une incohérence survient, mais jamais dans la formulation des questions, qui restent professionnelles 
            et neutres. Si """ + utilisateur + """ pose une question en cours de route, tu y réponds brièvement, puis le réfères
            à la section chatbot du site pour une réponse plus complète ou une discussion approfondie, avant de revenir 
            automatiquement au questionnaire. À la fin, tu génères un rapport personnalisé décrivant le type d’investisseur, 
            les comportements financiers observés, et une suggestion de répartition de portefeuille, 
            avec la possibilité de recommencer avec des questions plus avancées. Le tout est adapté au contexte canadien, 
            avec des références en dollars canadiens ($ CAD), des produits financiers locaux et une logique conforme aux réalités du marché canadien.
            Finalement, tu demandes à """ + utilisateur + """ s'il veut refaire le questionnaire avec des questions plus 
            techniques pour apprendre à se connaitre davantage."""),
        ]

        reponse = ""
        # code google ai studio
        for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
        ):
            reponse += chunk.text


    #Code de restrictions généré sur Copilot
        #Saut à la ligne pour chaque choix de réponses
        reponse_finale = re.sub(r'(?<!<br>)\s*([a-d]\))', r'<br>\1', reponse)
        #Remplace les doubles <br> par <br> simple
        reponse_finale = re.sub(r'(<br>\s*){2,}', r'<br>', reponse_finale)
        #Remplace **  et * par <br>
        reponse_finale = re.sub(r'\*\*', r'<br>', reponse_finale)
        reponse_finale = re.sub(r'\*', r'<br>', reponse_finale)
        #Met les questions en gras (et majuscule)
        reponse_finale = re.sub(r'(Question \d+.*?\?)', r'<strong>\1</strong>', reponse_finale, flags=re.DOTALL)
        reponse_finale = re.sub(r'Question (\d+)', r'QUESTION \1', reponse_finale)

        historique.append({"role": "model", "text": reponse})
        request.session['historique2'] = historique

        return reponse_finale

