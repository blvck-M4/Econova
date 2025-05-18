import datetime
import json

from django.conf import settings
from dotenv import load_dotenv

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
def listeActions():
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""Génère une liste du top 10 des actions sous la forme {symbole,nom,prix,
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
            tendance = tendance.strip("\n\r\t")
            actions.append({"symbole": symbole, "nom": nom, "prix": prix, "risque": risque, "tendance": tendance})
    print(actions)
    return actions

liste_donnees = []
def graphSimulation(action):
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""Génère une liste de données pour créer un graphique de prix par mois 
                sur 6 mois de l'action """ + action['nom'] + """. sous 
                ce format: [['2020-01-01',100.05];['2020-02-01',101.23]]). Fait le en considérant sa tendance (""" +
                                          action['tendance'] + """) et 
                son prix initial (""" + action['prix'] + """)""",)
            ],
        ),

    ]
    generate_content_config.system_instruction = [
        types.Part.from_text(text="""Tu es un générateur de liste de données de graphique. Tu n'écris rien d'autre 
        que la liste. Sépare les liste par ; et l'intérieur des listes par une virgule sans 
                utilisé rien d'autre pour que je puisse réutiliser la liste facilement. Ne me pas de signe $ sur le 
                prix.
                """),
    ]
    reponse = ""

    global liste_donnees
    for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
    ):
        reponse += chunk.text
    liste_donnees = reponse.split(';')

    donnees = []
    for donnee in liste_donnees:
        date, prix = donnee.split(',')
        date = date.strip("[]' \n\r\t")
        prix = prix.strip("[]' \n\r\t")
        donnees.append({"date": date, "prix": prix})
    return donnees


def simulationAI():


    return ""

def build_profile(member):
    """Construit un dict JSON du profil, avec timestamp pour varier le prompt."""
    dettes = []
    objectifs = []
    if member.dette_credits:
        dettes.append("Dettes de crédit")

    if member.dette_pret_etudiant:
        dettes.append("Dettes de pret etudiant")

    if member.epargne_etudes:
        dettes.append("Dettes de epargne")

    if member.dette_pret_automobile:
        dettes.append("Dettes de pret automobile")

    if member.dette_hypotheque:
        dettes.append("Dettes de hypotheque")

    if member.dette_autre is not None:
        dettes.append(member.dette_autre)

    objectifs = []



    return {
        "nom":        f"{member.prenom} {member.nom_de_famille}",
        "revenu":     member.revenu_mensuelle,
        "dettes": {
            "consommation": member.dette_credits,
            "étudiant":     member.dette_pret_etudiant,
            "auto":         member.dette_pret_automobile,
            "hypothèque":   member.dette_hypotheque,
            "autre":        member.dette_autre,
        },
        "objectifs": {
            "maison":        member.acheter_maison,
            "retraite":      member.preparation_retraite,
            "urgence":       member.fond_urgence,
            "remboursement": member.rembourser_dettes,
            "études":        member.epargne_etudes,
            "passif":        member.revenue_passif,
            "indépendance":  member.independance_financier,
            "investir":      member.investir,
            "autre":         member.autre_objectif,
        },
        "tolérance_risque": member.tolerance_risque,
    }

def get_conseil(member):
    profile_json = json.dumps(build_profile(member), ensure_ascii=False, indent=2)

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""Parmi les données du """+ f"Profil :\n{profile_json}" +""" choisi à l'hazard UNE des objectifs spécifique ou une des dettes spécifique parmi celles qui s'applique à l'utilisateur augmantant la probabilité
                de la génération d'une dettes et génère un conseil extêmement précise concernant cette dernière. Énumère pas les dettes de l'utilisateur. Le conseil ne doit pas dépasser plus de 100 mots. Elle soit est concise et pertinent
                ne vous présentez pas, donne directement le conseil. Ne travail pas en fonction de priorité cependant si tu choisi quelque chose à priorisé souligne rapidement l'importance""")

            ],
        ),

    ]
    generate_content_config.system_instruction = [
        types.Part.from_text(text="""
            Vous êtes NOVA, un conseiller financier certifié. Qui génère des conseils objectives. Vos conseils sont fourit
            à la troisième personne avec un ton neutre.
              
            """.strip()),
    ]
    reponse = ""

    global liste_donnees
    for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
    ):
        reponse += chunk.text

    return reponse





