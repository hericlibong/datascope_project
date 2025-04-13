from core.nlp_utils import (
    get_nlp, extract_named_entities,
    extract_numbers_and_units, extract_dates,
    extract_strong_verbs, format_entities,
    compute_datafication_score,
    group_named_entities,
    interpret_datafication_score,
    get_article_profile
)
import spacy.language


def test_get_nlp_returns_spacy_pipeline():
    nlp_fr = get_nlp("fr")
    nlp_en = get_nlp("en")
    nlp_unknown = get_nlp("de")

    assert isinstance(nlp_fr, spacy.language.Language)
    assert isinstance(nlp_en, spacy.language.Language)
    assert isinstance(nlp_unknown, spacy.language.Language)

    # Le fallback retourne bien le modèle français
    assert nlp_unknown is nlp_fr


def test_extract_named_entities_french():
    text = "Emmanuel Macron est allé à Bruxelles le 2 février."
    entities = extract_named_entities(text, language="fr")

    assert isinstance(entities, list)
    assert any(ent["text"] == "Emmanuel Macron" and ent["label"] == "PER" for ent in entities)
    assert any(ent["text"] == "Bruxelles" and ent["label"] == "LOC" for ent in entities)


def test_extract_named_entities_english():
    text = "Barack Obama visited Washington on February 2nd."
    entities = extract_named_entities(text, language="en")

    assert isinstance(entities, list)
    assert any(ent["text"] == "Barack Obama" and ent["label"] == "PERSON" for ent in entities)
    assert any(ent["text"] == "Washington" and ent["label"] in {"GPE", "LOC"} for ent in entities)
    assert any("February" in ent["text"] and ent["label"] == "DATE" for ent in entities)


def test_extract_numbers_and_units_basic_cases():
    text = "Le séisme de 7,9 de magnitude a fait 43 morts et détruit un immeuble de 30 étages."
    results = extract_numbers_and_units(text)

    assert isinstance(results, list)
    assert {"value": 7.9, "unit": "magnitude"} in [{"value": r["value"], "unit": r["unit"]} for r in results]
    assert {"value": 43, "unit": "morts"} in [{"value": r["value"], "unit": r["unit"]} for r in results]
    assert {"value": 30, "unit": "étages"} in [{"value": r["value"], "unit": r["unit"]} for r in results]


def test_extract_numbers_and_units_excludes_auxiliaries():
    text = "Il a été vu par 2 personnes. Elle est 1."
    results = extract_numbers_and_units(text)

    # Aucun de ces cas ne doit être retenu
    for r in results:
        assert r["unit"] not in {"a", "est", "été"}


def test_extract_dates_detects_multiple_formats():
    text = "Le vote a eu lieu le 03/02/2023. Une révision est prévue le 15/04/2024."
    results = extract_dates(text, language="fr")

    assert isinstance(results, list)
    extracted_texts = [r["text"] for r in results]
    extracted_iso = [r["parsed_date"] for r in results]

    assert "03/02/2023" in extracted_texts
    assert "15/04/2024" in extracted_texts
    assert any("2023-02-03" in iso for iso in extracted_iso)
    assert any("2024-04-15" in iso for iso in extracted_iso)


def test_extract_dates_ignores_invalid_inputs():
    text = "Demain ou après-demain peut-être."
    results = extract_dates(text, language="fr")
    assert results == []


def test_extract_strong_verbs_detects_known_lemmas():
    text = "Le président a provoqué un séisme. Il condamne l’attentat."
    results = extract_strong_verbs(text, language="fr")

    lemmas = [r["lemma"] for r in results]
    assert "provoquer" in lemmas
    assert "condamner" in lemmas
    for item in results:
        assert isinstance(item["text"], str)
        assert isinstance(item["lemma"], str)
        assert isinstance(item["start"], int)
        assert isinstance(item["end"], int)


def test_extract_strong_verbs_ignores_non_matching_verbs():
    text = "Il dort paisiblement. Elle pense à ses vacances."
    results = extract_strong_verbs(text, language="fr")

    assert isinstance(results, list)
    assert results == []  # Aucun verbe fort


def test_format_entities_aggregates_all_extractors():
    text = "Le 5 mai, Emmanuel Macron a provoqué 2 incidents à Paris."
    results = format_entities(text, language="fr")

    assert isinstance(results, dict)
    assert set(results.keys()) == {"named_entities", "numbers", "dates", "strong_verbs"}

    assert isinstance(results["named_entities"], list)
    assert isinstance(results["numbers"], list)
    assert isinstance(results["dates"], list)
    assert isinstance(results["strong_verbs"], list)

    # Vérifie que chaque liste contient au moins un élément
    assert any(ent["text"] == "Emmanuel Macron" for ent in results["named_entities"])
    assert any(n["value"] == 2 for n in results["numbers"])
    assert any("mai" in d["text"] for d in results["dates"])
    assert any(v["lemma"] == "provoquer" for v in results["strong_verbs"])


def test_compute_datafication_score_high():
    text = "Emmanuel Macron a annoncé 2 mesures et 1 loi à Paris le 4 avril."
    entities = {
        "named_entities": [{"text": "Emmanuel Macron", "label": "PER"}, {"text": "Paris", "label": "LOC"}],
        "numbers": [{"value": 2, "unit": "mesures"}, {"value": 1, "unit": "loi"}],
        "dates": [{"text": "4 avril", "parsed_date": "2024-04-04"}],
        "strong_verbs": [{"lemma": "annoncer"}]
    }

    result = compute_datafication_score(entities, text)

    assert result["score"] >= 9
    assert any("Plusieurs données chiffrées" in j for j in result["justifications"])
    assert any("Entités nommées multiples" in j for j in result["justifications"])
    assert any("Date(s) clairement identifiée(s)" in j for j in result["justifications"])
    assert any("Verbe(s) fort(s)" in j for j in result["justifications"])


def test_compute_datafication_score_low_density_penalty():
    text = "Ceci est un long texte narratif sans beaucoup d’éléments datafiables. " * 50
    entities = {
        "named_entities": [{"text": "Quelqu’un", "label": "PER"}],
        "numbers": [],
        "dates": [],
        "strong_verbs": []
    }

    result = compute_datafication_score(entities, text)

    assert result["score"] <= 2
    assert "Faible densité" in " ".join(result["justifications"])
    assert result["density"] < 0.01


def test_group_named_entities_counts_occurrences_by_label():
    entities = [
        {"text": "Paris", "label": "LOC"},
        {"text": "Paris", "label": "LOC"},
        {"text": "Emmanuel Macron", "label": "PER"},
        {"text": "Paris", "label": "LOC"},
        {"text": "Emmanuel Macron", "label": "PER"},
    ]

    grouped = group_named_entities(entities)

    assert isinstance(grouped, dict)
    assert "LOC" in grouped
    assert "PER" in grouped
    assert grouped["LOC"]["Paris"] == 3
    assert grouped["PER"]["Emmanuel Macron"] == 2


def test_interpret_datafication_score_ranges():
    assert interpret_datafication_score(10).startswith("Très bon potentiel")
    assert interpret_datafication_score(8).startswith("Bon potentiel")
    assert interpret_datafication_score(5).startswith("Potentiel modéré")
    assert interpret_datafication_score(3).startswith("Faible potentiel")
    assert interpret_datafication_score(0).startswith("Très faible")


def test_get_article_profile_datajournalisme_eleve():
    entities = {
        "strong_verbs": [{}, {}],
        "numbers": [{}, {}, {}],
        "dates": [{}],
        "named_entities": [{"label": "LOC"}, {"label": "LOC"}]
    }
    score_data = {"score": 9, "density": 0.2}
    result = get_article_profile(entities, score_data)
    assert result.startswith("📊")


def test_get_article_profile_localise_temporel():
    entities = {
        "strong_verbs": [],
        "numbers": [{}, {}, {}],
        "dates": [{}, {}],
        "named_entities": [{"label": "LOC"}, {"label": "LOC"}]
    }
    score_data = {"score": 6, "density": 0.1}
    result = get_article_profile(entities, score_data)
    assert result.startswith("📍")


def test_get_article_profile_narratif_descriptif():
    entities = {
        "strong_verbs": [],
        "numbers": [{}],
        "dates": [],
        "named_entities": [{"label": "PER"}]
    }
    score_data = {"score": 2, "density": 0.02}
    result = get_article_profile(entities, score_data)
    assert result.startswith("📣")


def test_get_article_profile_structure_quantifiable():
    entities = {
        "strong_verbs": [],
        "numbers": [{}],
        "dates": [{}],
        "named_entities": [{"label": "LOC"}, {"label": "LOC"}]
    }
    score_data = {"score": 7, "density": 0.08}
    result = get_article_profile(entities, score_data)
    assert result.startswith("🧮")


def test_get_article_profile_exploratoire():
    entities = {
        "strong_verbs": [],
        "numbers": [],
        "dates": [],
        "named_entities": [{"label": "PER"}]
    }
    score_data = {"score": 4, "density": 0.05}
    result = get_article_profile(entities, score_data)
    assert result.startswith("🔬")


def test_extract_numbers_excludes_unit_est():
    text = "Le score est 12 points."
    results = extract_numbers_and_units(text)
    # Ici le match regex serait : "12 points" → donc ne teste pas "est"
    # Il faut une forme comme :
    text = "12 est un nombre."
    results = extract_numbers_and_units(text)
    assert results == []  # "est" est dans les unités exclues
