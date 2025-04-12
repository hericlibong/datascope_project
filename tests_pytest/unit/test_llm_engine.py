import pytest
from core.llm_engine import(
    build_enriched_prompt, call_openai, 
    generate_journalistic_angles, suggest_datasets_llm,
    parse_markdown_list
)
from unittest.mock import MagicMock, patch

def test_build_enriched_prompt_structure_and_content():
    # Entrées simulées
    text = "Voici un test de texte. Emmanuel Macron a annoncé 200 millions d’euros le 5 mai."
    entities = {
        "named_entities": [{"text": "Emmanuel Macron", "label": "PER"}],
        "numbers": [{"value": "200", "unit": "millions d’euros"}],
        "dates": [{"text": "5 mai"}],
        "strong_verbs": [{"lemma": "annoncer"}]
    }

    messages = build_enriched_prompt(text, entities)

    # Vérifications
    assert isinstance(messages, list)
    assert len(messages) == 2

    system_msg, user_msg = messages

    # Vérifier le format de chaque message
    assert "role" in system_msg and "content" in system_msg
    assert "role" in user_msg and "content" in user_msg
    assert system_msg["role"] == "system"
    assert user_msg["role"] == "user"

    # Vérifie que les entités sont bien présentes dans le message
    user_content = user_msg["content"]
    assert "Emmanuel Macron" in user_content
    assert "200 millions d’euros" in user_content
    assert "5 mai" in user_content
    assert "annoncer" in user_content


def test_call_openai_returns_text_without_api_call():
    # 1. Création d'une réponse simulée
    fake_response = MagicMock()
    fake_response.choices[0].message.content = "Réponse simulée."

    # 2. Patch du client OpenAI dans le module testé
    with patch("core.llm_engine.client.chat.completions.create", return_value=fake_response):
        messages = [{"role": "user", "content": "Hello"}]
        result = call_openai(messages)

    # 3. Vérification
    assert isinstance(result, str)
    assert result == "Réponse simulée."




def test_generate_journalistic_angles_mocked_response():
    article = "Le président a déclaré une nouvelle politique le 2 février avec un budget de 50 millions d’euros."

    fake_entities = {
        "named_entities": [{"text": "président", "label": "PER"}],
        "numbers": [{"value": "50", "unit": "millions d’euros"}],
        "dates": [{"text": "2 février"}],
        "strong_verbs": [{"lemma": "déclarer"}]
    }

    with patch("core.llm_engine.format_entities", return_value=fake_entities), \
         patch("core.llm_engine.call_openai", return_value="Angle 1. Angle 2. Angle 3."):

        result = generate_journalistic_angles(article)

    assert isinstance(result, str)
    assert "Angle" in result


def test_suggest_datasets_llm_mocked_response():
    text = "L'article parle de pollution à Paris le 12 mai avec 100 µg/m³ relevés dans l'air ambiant."
    entities = {
        "named_entities": [{"text": "Paris", "label": "LOC"}],
        "numbers": [{"value": "100", "unit": "µg/m³"}],
        "dates": [{"text": "12 mai"}]
    }

    with patch("core.llm_engine.call_openai", return_value="Dataset A. Dataset B. Dataset C."):
        result = suggest_datasets_llm(text, entities)

    assert isinstance(result, str)
    assert "Dataset" in result


def test_parse_markdown_list_extracts_titles_and_contents():
    markdown_input = (
        "1. **Qualité de l'air en Europe** : Analyser les niveaux de pollution dans les grandes villes européennes.\n"
        "2. **Impact des ZFE** : Étudier les effets des Zones à Faibles Émissions sur la santé publique.\n"
        "3. **Politiques environnementales** : Comparer les stratégies de réduction de la pollution dans différents pays.\n"
    )

    results = parse_markdown_list(markdown_input)

    assert isinstance(results, list)
    assert len(results) == 3

    assert results[0]["title"] == "Qualité de l'air en Europe"
    assert "pollution" in results[0]["content"]

    assert results[1]["title"] == "Impact des ZFE"
    assert "Zones à Faibles Émissions" in results[1]["content"]

    assert results[2]["title"] == "Politiques environnementales"
    assert "réduction de la pollution" in results[2]["content"]


def test_call_openai_handles_exception_gracefully():
    # 1. Forcer une exception sur l'appel API
    with patch("core.llm_engine.client.chat.completions.create", side_effect=Exception("Simulated failure")):
        messages = [{"role": "user", "content": "Hello"}]
        result = call_openai(messages)

    # 2. Vérification du message d'erreur
    assert isinstance(result, str)
    assert result.startswith("[ERREUR LLM]")
    assert "Simulated failure" in result


