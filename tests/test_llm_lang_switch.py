import sys
from pathlib import Path

# Ajoute le dossier racine du projet à sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.llm_engine import generate_journalistic_angles, suggest_datasets_llm
from core.nlp_utils import format_entities

def test_llm_in_french():
    text = """
    En 2022, plus de 45 % de l’électricité produite en France provenait de sources renouvelables. 
    Le gouvernement a annoncé un plan d’investissement de 30 milliards d’euros dans l’éolien offshore.
    """
    print("\n🟦 [FR] Angles :")
    print(generate_journalistic_angles(text, language="fr"))

    entities = format_entities(text, language="fr")
    print("\n🟦 [FR] Sources :")
    print(suggest_datasets_llm(text, entities, language="fr"))


def test_llm_in_english():
    text = """
    In 2023, more than 60% of electricity in the UK came from renewable sources. 
    The British government announced a 50 billion pound investment plan in solar and offshore wind energy.
    """
    print("\n🟥 [EN] Angles :")
    print(generate_journalistic_angles(text, language="en"))

    entities = format_entities(text, language="en")
    print("\n🟥 [EN] Sources :")
    print(suggest_datasets_llm(text, entities, language="en"))


if __name__ == "__main__":
    test_llm_in_french()
    test_llm_in_english()
