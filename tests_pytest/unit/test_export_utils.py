from core.export_utils import export_analysis_to_markdown


def test_export_analysis_to_markdown_creates_valid_structure():
    text = "Exemple d’article simple."
    score = {"score": 8, "density": 0.1, "structured_items": 4, "word_count": 40}
    comment = "Bon potentiel de datafication"
    profile = "📍 Localisé et temporel"
    entities = {
        "named_entities": [{"text": "Paris", "label": "LOC"}],
        "numbers": [{"value": 2, "unit": "projets"}],
        "dates": [{"text": "4 avril"}],
        "strong_verbs": [{"lemma": "annoncer"}]
    }
    angles = "1. **Angle 1** : Analyse des projets à Paris.\n2. **Angle 2** : Historique des annonces."
    sources = "1. [INSEE](https://insee.fr)\n2. [Data.gouv.fr](https://data.gouv.fr)"

    md_output = export_analysis_to_markdown(text, score, comment, profile, entities, angles, sources)

    assert isinstance(md_output, str)
    assert "# 📄 Résultat de l’analyse DataScope" in md_output
    assert "## 🧾 Texte analysé" in md_output
    assert "## 📊 Score de datafication" in md_output
    assert "- Score : **8/10**" in md_output
    assert "Paris (LOC)" in md_output
    assert "2 projets" in md_output
    assert "annoncer" in md_output
    assert "## 🧭 Suggestions d’angles journalistiques" in md_output
    assert "## 🌐 Suggestions de sources / datasets" in md_output
    assert "[INSEE]" in md_output


def test_export_analysis_handles_empty_entities():
    text = "Texte sans structure"
    score = {"score": 2, "density": 0.01, "structured_items": 0, "word_count": 100}
    comment = "Très faible"
    profile = "📣 Narratif"
    entities = {}  # aucune entité fournie
    angles = "Aucun angle pertinent détecté."
    sources = "Aucune source pertinente identifiée."

    output = export_analysis_to_markdown(text, score, comment, profile, entities, angles, sources)

    assert isinstance(output, str)
    assert "## 🧭 Suggestions d’angles journalistiques" in output
    assert "## 🌐 Suggestions de sources / datasets" in output
    assert "Aucun angle pertinent détecté." in output
