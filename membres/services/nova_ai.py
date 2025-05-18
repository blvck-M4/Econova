from django.conf import settings
from dotenv import load_dotenv

import os
from google import genai
from google.genai import types

from membres.models import Membre

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

def reponseBot (request, utilisateur):
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
        contents = [
            types.Content(role=message["role"] if message["role"] == "user" else "model", parts=[types.Part.from_text(
                text=message["text"])])
            for message in historique

        ]
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


def conseilActions(stock_data, profil):
    nom = ''
    if stock_data:
        nom = stock_data['name']
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""Donne moi des conseils financiers par rapport l'action 
                """ + 'AAPL' + """. Fait le sachant que j'ai un profil financier """+profil),
            ],
        ),

    ]
    generate_content_config.system_instruction = [
        types.Part.from_text(text="""Tu es NOVA, un conseiller financier virtuel intelligent conçu pour 
                                    accompagner un utilisateur d’EcoNova dans la gestion et l’optimisation de ses 
                                    finances personnelles. Ne donne pas des réponses trop longues, donc de plus de 500 
                                    mots. Si tu rajoutes des points numérotés, fait le après les *.
                                    """),
    ]
    reponse = ""
    for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
    ):
        reponse += chunk.text
    reponse_finale = reponse.replace('*', '<br>')
    return reponse_finale


liste_actions = []
liste_cryptos = []
def listeProduits(produit):
    if produit == 'actions':
        format = 'AAPL'
    elif produit == 'cryptomonnaies':
        format = 'BTC-USD'
    else:
        format = ''
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""Génère le symbol du top 10 des """+produit+""" sous la forme {
                """+format+""",
                ...}"""),
            ],
        ),

    ]
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
        for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
        ):
            reponse += chunk.text
        liste_produits = [produit.strip() for produit in reponse.split(',')]



    print(liste_produits)
    return liste_produits




