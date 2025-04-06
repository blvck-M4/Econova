from django.conf import settings
from dotenv import load_dotenv
load_dotenv()
import os
from google import genai
from google.genai import types

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
                                finances personnelles. Propulsé par l’intelligence artificielle, NOVA analyse les habitudes financières des utilisateurs et 
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
def listeActions():
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""Génère une liste du top 50 des actions sous la forme {symbole,nom,prix,
                niveau de 
                risque,tendance; ...}"""),
            ],
        ),

    ]
    generate_content_config.system_instruction = [
        types.Part.from_text(text="""Tu es un générateur de liste d'actions en français. Tu n'écris rien d'autre que la 
        liste 
            et tu donnes les prix en $CAN. Sépare les liste par ; et l'intérieur des listes par une virgule sans 
            utilisé rien d'autre pour que je puisse réutiliser la liste facilement. Aussi met la tendance sous ce 
            format: -2.39 (-1.44 %) les six derniers mois. N'inverse pas les noms et les 
            symboles des actions. Les symboles sont générralement moins de 4 lettres."""),
    ]
    reponse = ""
    global liste_actions
    if len(liste_actions) == 0:
        for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
        ):
            reponse += chunk.text
        liste_actions = reponse.split(';')

    actions = []
    for action in liste_actions:
        symbole, nom, prix, risque, tendance = action.split(',')
        if len(symbole.strip()) <= 5:
            actions.append({"symbole": symbole, "nom": nom, "prix": prix, "risque": risque, "tendance": tendance})
    print(actions)
    return actions


def simulationAI():


    return ""
