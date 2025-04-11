import spacy
from typing import List, Dict
import re
import dateparser
from  .strongs_words import strongs_verbs
from collections import defaultdict, Counter

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


def extract_numbers_and_units(text: str) -> List[Dict]:
    """
    Extrait les nombres suivis de mots (unités), en filtrant les faux positifs.
    Exemples : '43 ouvriers', '30 étages', '7.9 de magnitude'
    """
    # Regex : nombre avec , ou . + mot (éventuellement précédé de "de")
    pattern = r"\b(\d+(?:[.,]\d+)?)\s+(?:de\s+)?([a-zA-Zéèêçûîâà]+)"
    matches = re.finditer(pattern, text)

    # Mots à exclure comme unités (verbes, auxiliaires, etc.)
    EXCLUDED_UNITS = {"a", "est", "sont", "ont", "été", "sera", "seront", "avoir", "être"}

    results = []
    for match in matches:
        unit = match.group(2).lower()
        if unit in EXCLUDED_UNITS:
            continue

        value = match.group(1).replace(",", ".")  # 7,9 → 7.9
        try:
            value = float(value) if "." in value else int(value)
        except ValueError:
            continue

        results.append({
            "value": value,
            "unit": unit,
            "start": match.start(),
            "end": match.end(),
        })

    return results


def extract_dates(text: str, language: str = "fr") -> List[Dict]:
    """
    Extrait les dates à partir du texte, sous divers formats.
    Utilise regex + dateparser pour fiabiliser la conversion.
    """
    # Expressions classiques : 2 février, 03/04/2025, mars 2023, le 10 janvier
    pattern = r"\b(?:le\s+)?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}\s+[a-zéû]+|[a-zéû]+\s+\d{4})\b"
    matches = re.finditer(pattern, text, flags=re.IGNORECASE)

    results = []
    for match in matches:
        date_str = match.group(1)
        parsed = dateparser.parse(date_str, languages=[language])

        if parsed:
            results.append({
                "text": date_str,
                "parsed_date": parsed.isoformat(),
                "start": match.start(),
                "end": match.end(),
            })

    return results


def extract_strong_verbs(text: str, language: str = "fr") -> List[Dict]:
    """
    Extrait les verbes forts présents dans le texte en les comparant
    avec la liste de strongs_verbs. Utilise la lemmatisation pour fiabilité.
    """
    nlp = get_nlp(language)
    doc = nlp(text)

    strong_hits = []
    for token in doc:
        # Vérifie si le token est un verbe et si sa forme de base est dans strongs_verbs
        if token.pos_ == "VERB":
            lemma = token.lemma_.lower()
            if lemma in strongs_verbs:
                strong_hits.append({
                    "text": token.text,
                    "lemma": lemma,
                    "start": token.idx,
                    "end": token.idx + len(token.text)
                })

    return strong_hits

def format_entities(text: str, language: str = "fr") -> Dict:
    """
    Regroupe toutes les entités extraites dans un dictionnaire lisible.
    """
    return {
        "named_entities": extract_named_entities(text, language),
        "numbers": extract_numbers_and_units(text),
        "dates": extract_dates(text, language),
        "strong_verbs": extract_strong_verbs(text, language),
    }

def compute_datafication_score(entities: Dict, text: str) -> Dict:
    """
    Calcule un score de "datafication" pour un texte donné en fonction des entités détectées
    et de la densité de contenu structuré. Le score est modulé par un facteur de crédibilité
    basé sur la densité d'information.

    Args:
        entities (Dict): Un dictionnaire contenant des listes d'entités détectées, 
                         telles que "numbers", "dates", "named_entities", et "strong_verbs".
        text (str): Le texte à analyser.

    Returns:
        Dict: Un dictionnaire contenant :
            - "score" (int): Le score de datafication (maximum 10).
            - "justifications" (List[str]): Les raisons expliquant le score attribué.
            - "density" (float): La densité de contenu structuré par rapport au nombre de mots.
            - "structured_items" (int): Le nombre total d'éléments structurés détectés.
            - "word_count" (int): Le nombre total de mots dans le texte.
    """
    score = 0
    justifications = []

    total_items = sum(len(v) for v in entities.values())

    if len(entities.get("numbers", [])) >= 2:
        score += 3
        justifications.append("Plusieurs données chiffrées détectées")

    if len(entities.get("dates", [])) >= 1:
        score += 2
        justifications.append("Date(s) clairement identifiée(s)")

    if len(entities.get("named_entities", [])) >= 2:
        score += 2
        justifications.append("Entités nommées multiples (lieux, personnes, org)")

    if len(entities.get("strong_verbs", [])) >= 1:
        score += 2
        justifications.append("Verbe(s) fort(s) signalant un impact ou une action")

    # Pondération selon la densité de contenu structuré
    words = len(text.split())
    density = total_items / words if words else 0

    if density < 0.01:
        score = max(score - 2, 0)
        justifications.append("Faible densité d'information datafiable pour la longueur de l'article")

    return {
        "score": min(score, 10),
        "justifications": justifications,
        "density": round(density, 3),
        "structured_items": total_items,
        "word_count": words
    }

def group_named_entities(entities: list[dict]) -> dict:
    grouped = defaultdict(Counter)
    for ent in entities:
        label = ent["label"]
        text = ent["text"]
        grouped[label][text] += 1
    return grouped


def interpret_datafication_score(score: int) -> str:
    if score >= 9:
        return "Très bon potentiel de datajournalisme (chiffré, localisé, visualisable)"
    elif score >= 7:
        return "Bon potentiel de datafication avec éléments structurés exploitables"
    elif score >= 5:
        return "Potentiel modéré : quelques éléments chiffrés ou datés identifiables"
    elif score >= 3:
        return "Faible potentiel data : surtout narratif, peu structuré"
    else:
        return "Très faible ou absent : article descriptif sans données exploitables"


def get_article_profile(entities: dict, score_data: dict) -> str:
    """
    Génère un profil éditorial basé sur les entités, la densité, et le score de datafication.
    """
    n_verbs = len(entities.get("strong_verbs", []))
    n_numbers = len(entities.get("numbers", []))
    n_dates = len(entities.get("dates", []))
    n_places = sum(1 for ent in entities.get("named_entities", []) if ent["label"] == "LOC")
    density = score_data.get("density", 0)
    score = score_data.get("score", 0)

    if score >= 9 and density > 0.15 and n_verbs >= 2:
        return "📊 Datajournalisme potentiel élevé – structuré, chiffré et dynamique"
    elif n_numbers >= 3 and n_dates >= 2 and n_places >= 2:
        return "📍 Localisé et temporel – structuré autour de données concrètes"
    elif n_numbers <= 1 and n_verbs == 0 and density < 0.05:
        return "📣 Narratif ou descriptif – peu de données exploitables"
    elif score >= 6 and n_places >= 2 and n_verbs == 0:
        return "🧮 Structuré et quantifiable – intéressant pour un angle local"
    else:
        return "🔬 Exploratoire ou symbolique – sujet riche mais peu structuré"
