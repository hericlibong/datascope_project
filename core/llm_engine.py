import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from core.nlp_utils import format_entities
import markdown

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


def build_enriched_prompt(text: str, entities: dict, language: str = "fr") -> list[dict]:
    named_entities = ", ".join(ent["text"] for ent in entities.get("named_entities", []))
    numbers = ", ".join(f"{n['value']} {n['unit']}" for n in entities.get("numbers", []))
    dates = ", ".join(d["text"] for d in entities.get("dates", []))
    strong_verbs = ", ".join(v["lemma"] for v in entities.get("strong_verbs", []))

    if language == "en":
        system_message = {
            "role": "system",
            "content": "You are a journalism assistant. You help identify data-driven story angles from facts, figures, and key entities."
        }
        user_message = {
            "role": "user",
            "content": (
                f"Here is an article to analyze:\n{text[:2000]}\n\n"
                f"The article includes the following extracted elements:\n"
                f"- Named entities: {named_entities}\n"
                f"- Quantitative data: {numbers}\n"
                f"- Dates: {dates}\n"
                f"- Impact verbs: {strong_verbs}\n\n"
                f"Suggest 3 actionable data-driven story angles as a numbered list."
            )
        }
    else:  # FR par défaut
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


def generate_journalistic_angles(text: str, language: str = "fr") -> str:
    """
    Fonction centrale qui :
    - analyse le texte (NLP)
    - construit un prompt enrichi
    - appelle GPT pour générer des angles journalistiques
    """
    entities = format_entities(text, language)
    messages = build_enriched_prompt(text, entities, language)
    return call_openai(messages)


def suggest_datasets_llm(text: str, entities: dict, language: str = "fr") -> str:
    named_entities = ", ".join(ent["text"] for ent in entities.get("named_entities", []))
    numbers = ", ".join(f"{n['value']} {n['unit']}" for n in entities.get("numbers", []))
    dates = ", ".join(d["text"] for d in entities.get("dates", []))

    if language == "en":
        system_msg = "You are a research assistant specialized in open datasets and public data sources."
        user_msg = (
            f"Here is an article:\n{text[:2000]}\n\n"
            f"It includes:\n"
            f"- Named entities: {named_entities}\n"
            f"- Numbers: {numbers}\n"
            f"- Dates: {dates}\n\n"
            f"Suggest 3 to 5 relevant public datasets or platforms to enrich or verify the topic."
        )
    else:
        system_msg = "Tu es un assistant spécialisé en veille de sources ouvertes et datasets publics."
        user_msg = (
            f"Voici un article :\n{text[:2000]}\n\n"
            f"Il contient les éléments suivants :\n"
            f"- Entités : {named_entities}\n"
            f"- Données : {numbers}\n"
            f"- Dates : {dates}\n\n"
            f"Peux-tu me suggérer 3 à 5 plateformes ou bases de données publiques (françaises, internationales ou spécialisées) utiles pour documenter ou enrichir ce sujet ?"
        )

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg}
    ]

    return call_openai(messages)


def suggest_visualizations_llm(angles: list[dict], language="fr") -> str:
    """
    Génère des suggestions de visualisation pour chaque angle éditorial.
    """
    prompt = "Voici des angles éditoriaux proposés :\n"
    for idx, angle in enumerate(angles, 1):
        prompt += f"{idx}. {angle['title']}\n"

    if language == "en":
        instruction = (
            "For each angle above, suggest 1 or 2 relevant types of data visualizations "
            "and explain why these would support the story. Clearly link each visualization suggestion to the corresponding angle."
        )
    else:
        instruction = (
            "Pour chaque angle ci-dessus, suggère une ou deux visualisations de données pertinentes "
            "et explique brièvement pourquoi elles soutiendraient bien l'analyse. Associe chaque suggestion à l'angle correspondant."
        )

    messages = [
        {"role": "system", "content": "You are a data visualization advisor for data journalism."},
        {"role": "user", "content": prompt + "\n\n" + instruction}
    ]

    # Appel LLM pour générer les visualisations
    response = call_openai(messages)
    return response.strip()


def parse_markdown_list(raw_text: str) -> list:
    """
    Extrait une liste structurée depuis un texte markdown GPT
    et transforme le contenu en HTML.
    """
    entries = re.findall(r"\d+\.\s+\*\*(.*?)\*\*\s*:\s*(.*?)\s*(?=\d+\.\s|\Z)", raw_text, re.DOTALL)
    return [
        {
            "title": title.strip(),
            "content": markdown.markdown(content.strip())  # 🔁 ici la transformation HTML
        }
        for title, content in entries
    ]
