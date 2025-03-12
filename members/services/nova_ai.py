from dotenv import load_dotenv
load_dotenv()
import os
from google import genai
from google.genai import types

client = genai.Client(
            api_key=os.getenv('GEMINI_API_KEY'),
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
        historique.append({"role": "model", "text": reponse})
        request.session['historique'] = historique

        return reponse


