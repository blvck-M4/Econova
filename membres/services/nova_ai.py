import json

from django.conf import settings
from dotenv import load_dotenv

load_dotenv()
import os
import re

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


def reponseBot(request, utilisateur):
    historique = request.session.get('historique', [])
    utilisateur_infos = ''
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
                """ + nom + """. Fait le sachant que j'ai un profil financier """ + profil),
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
        liste_actions = reponse.split(';')

    actions = []
    for action in liste_actions:
        symbole, nom, prix, risque, tendance = action.split(',')
        if len(symbole.strip()) <= 5:
            tendance = tendance.strip("\n\t\r")
            prix = prix.strip("\n\t\r")
            symbole = symbole.strip("\n\t\r")
            nom = nom.strip("\n\t\r")
            risque = risque.strip("\n\t\r")

            actions.append({"symbole": symbole, "nom": nom, "prix": prix, "risque": risque, "tendance": tendance})
    print(actions)
    return actions


import datetime
liste_donnees = []


def graphSimulation(action):
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""La date est """ + date + """. Génère une liste de données pour créer un graphique de prix par mois 
                sur les 6 derniers mois de l'action """ + action['nom'] + """. sous 
                ce format: [['2020-01-01',100.05];['2020-02-01',101.23]]). Fait le en considérant 
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

    print(liste_produits)
    return liste_produits

def simulationAI():
    return ""



#Programmation de l'IA du questionnaire de profil d'investisseur dans la section EDUCATION
def qstProfil(request, utilisateur):
    historique = request.session.get('historique2', [])

    if request.method == "POST":
        user_message = request.POST.get("message")
        historique.append({"role": "user", "text": user_message})

        contents = [
            types.Content(role=message["role"] if message["role"] == "user" else "model",
                          parts=[types.Part.from_text(text=message["text"])])
            for message in historique
        ]

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
        for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
        ):
            reponse += chunk.text

        reponse = re.sub(r'<br\s*/?>', '', reponse)

        reponse_finale = re.sub(r'(Question)( \d+.*\?)', lambda m: f'<strong>{m.group(1).upper()}{m.group(2)}</strong>', reponse)

        reponse_finale = re.sub(r'(?<!<br>)\s*([a-d]\))', r'<br>\1', reponse_finale)
        reponse_finale = re.sub(r'(<br>\s*){2,}', r'<br>', reponse_finale)
        reponse_finale = re.sub(r'\*\*', r'<br>', reponse_finale)
        reponse_finale = re.sub(r'\*', r'<br>', reponse_finale)
        reponse_finale = re.sub(r'(Question \d+:)(?!\s*(<br>|<br\s*/?>))', r'\1<br>', reponse_finale)

        print("Contenu après modification:")
        print(reponse_finale)

        historique.append({"role": "model", "text": reponse})
        request.session['historique2'] = historique

        return reponse_finale


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
        "nom": f"{member.prenom} {member.nom_de_famille}",
        "revenu": member.revenu_mensuelle,
        "dettes": {
            "consommation": member.dette_credits,
            "étudiant": member.dette_pret_etudiant,
            "auto": member.dette_pret_automobile,
            "hypothèque": member.dette_hypotheque,
            "autre": member.dette_autre,
        },
        "objectifs": {
            "maison": member.acheter_maison,
            "retraite": member.preparation_retraite,
            "urgence": member.fond_urgence,
            "remboursement": member.rembourser_dettes,
            "études": member.epargne_etudes,
            "passif": member.revenue_passif,
            "indépendance": member.independance_financier,
            "investir": member.investir,
            "autre": member.autre_objectif,
        },
        "tolérance_risque": member.tolerance_risque,
    }


def get_conseil(member):
    profile_json = json.dumps(build_profile(member), ensure_ascii=False, indent=2)

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""Parmi les données du """ + f"Profil :\n{profile_json}" + """ choisi à l'hazard UNE des objectifs spécifique ou une des dettes spécifique parmi celles qui s'applique à l'utilisateur augmantant la probabilité
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