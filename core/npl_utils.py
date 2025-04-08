import spacy
from typing import List, Dict

# Chargement des modèles au démarrage
MODELS = {
    "fr": spacy.load("fr_core_news_md"),
    "en": spacy.load("en_core_web_md"),
}

def get_nlp(language: str = "fr"):
    """Retourne le pipeline spaCy selon la langue choisie (fr ou en)."""
    return MODELS.get(language, MODELS["fr"])


def extract_named_entities(text: str, language: str = "fr") -> List[Dict]:
    """
    Extrait les entités nommées (personnes, lieux, dates, organisations, etc.)
    Retourne une liste de dictionnaires avec : texte, type, position.
    """
    nlp = get_nlp(language)
    doc = nlp(text)

    entities = []
    for ent in doc.ents:
        entities.append({
            "text": ent.text,
            "label": ent.label_,
            "start_char": ent.start_char,
            "end_char": ent.end_char,
        })

    return entities
