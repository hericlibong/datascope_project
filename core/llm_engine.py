import os
import re
from openai import OpenAI
from dotenv import load_dotenv

# Charge les variables d'environnement (.env)
load_dotenv()

# Initialisation du client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

def call_openai(messages: list[dict], model: str = OPENAI_MODEL, temperature: float = 0.7) -> str:
    """
    Envoie une requête à l'API OpenAI et renvoie la réponse (texte).
    Compatible avec l'API openai >= 1.0.0
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[ERREUR LLM] {e}"
    

def build_enriched_prompt(text: str, entities: dict) -> list[dict]:
    """
    Construit un prompt structuré pour OpenAI à partir du texte et des entités extraites.
    Retourne une liste de messages à envoyer à l'API OpenAI.
    """
    named_entities = ", ".join(ent["text"] for ent in entities.get("named_entities", []))
    numbers = ", ".join(f"{n['value']} {n['unit']}" for n in entities.get("numbers", []))
    dates = ", ".join(d["text"] for d in entities.get("dates", []))
    strong_verbs = ", ".join(v["lemma"] for v in entities.get("strong_verbs", []))

    system_message = {
        "role": "system",
        "content": "Tu es un assistant spécialisé en datajournalisme. Tu aides à identifier les angles éditoriaux exploitables à partir de faits, de données, et d'événements."
    }

    user_message = {
        "role": "user",
        "content": (
            f"Voici un article à analyser :\n{text[:2000]}\n\n"
            f"Le texte contient les éléments suivants extraits automatiquement :\n"
            f"- Entités nommées : {named_entities}\n"
            f"- Données chiffrées : {numbers}\n"
            f"- Dates : {dates}\n"
            f"- Verbes d'impact : {strong_verbs}\n\n"
            f"Génère 3 propositions d’angles journalistiques concrets, exploitables en datajournalisme, sous forme de liste."
        )
    }

    return [system_message, user_message]

from core.nlp_utils import format_entities


def generate_journalistic_angles(text: str, language: str = "fr") -> str:
    """
    Fonction centrale qui :
    - analyse le texte (NLP)
    - construit un prompt enrichi
    - appelle GPT pour générer des angles journalistiques
    """
    entities = format_entities(text, language)
    messages = build_enriched_prompt(text, entities)
    return call_openai(messages)


def suggest_datasets_llm(text: str, entities: dict) -> str:
    """
    Utilise GPT pour suggérer des plateformes, bases de données ou APIs
    pertinentes selon le contenu réel de l'article (sans codage thématique en dur).
    """
    named_entities = ", ".join(ent["text"] for ent in entities.get("named_entities", []))
    numbers = ", ".join(f"{n['value']} {n['unit']}" for n in entities.get("numbers", []))
    dates = ", ".join(d["text"] for d in entities.get("dates", []))

    messages = [
        {
            "role": "system",
            "content": "Tu es un assistant spécialisé en veille de sources ouvertes et datasets publics. Ton rôle est de suggérer des bases de données ou plateformes exploitables en lien avec le contenu analysé."
        },
        {
            "role": "user",
            "content": (
                f"Voici un article :\n{text[:2000]}\n\n"
                f"Il contient les éléments suivants :\n"
                f"- Entités : {named_entities}\n"
                f"- Données : {numbers}\n"
                f"- Dates : {dates}\n\n"
                f"Peux-tu me suggérer 3 à 5 plateformes ou bases de données publiques (françaises, internationales ou spécialisées) utiles pour documenter ou enrichir ce sujet ?"
            )
        }
    ]

    return call_openai(messages)



def parse_markdown_list(raw_text: str) -> list:
    """
    Extrait une liste structurée depuis un texte markdown GPT :
    "1. **Titre** : Contenu"
    """
    entries = re.findall(r"\d+\.\s+\*\*(.*?)\*\*\s*:\s*(.*?)\s*(?=\d+\.\s|\Z)", raw_text, re.DOTALL)
    return [{"title": title.strip(), "content": content.strip()} for title, content in entries]


