import pytest
from app import create_app  # ou directement depuis main.py si pas factorisé
import io

@pytest.fixture
def client():
    app = create_app()  # si tu as une factory, sinon importe l’app directe
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        yield client

def test_homepage_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Analyser un article" in response.data or b"form" in response.data

def test_analyze_route_with_text(client):
    payload = {"article_text": "Emmanuel Macron a annoncé 2 lois à Paris le 4 avril."}
    response = client.post("/analyze", data=payload)
    assert response.status_code == 200
    assert b"Score de datafication" in response.data

def test_about_page_loads(client):
    response = client.get("/about")
    assert response.status_code == 200
    assert b"A propos" in response.data or b"DataScope" in response.data

def test_analyze_with_uploaded_txt_file(client):
    data = {
        "article_file": (io.BytesIO("Le 3 avril, 45 blessés a Lyon.".encode("utf-8")), "test_article.txt")
    }
    response = client.post("/analyze", data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert b"Score de datafication" in response.data

def test_analyze_route_with_empty_text(client):
    response = client.post("/analyze", data={"article_text": ""})
    assert response.status_code == 200
    assert b"Aucun texte ou fichier valide fourni" in response.data

def test_download_route_returns_markdown(client):
    payload = {
        "article_text": "Texte test",
        "score": str({"score": 7, "density": 0.1, "structured_items": 4, "word_count": 40}),
        "score_comment": "Bon potentiel",
        "profile": "📍 Localisé",
        "entities": str({
            "named_entities": [{"text": "Paris", "label": "LOC"}],
            "numbers": [{"value": 2, "unit": "mesures"}],
            "dates": [{"text": "4 avril"}],
            "strong_verbs": [{"lemma": "annoncer"}]
        }),
        "angles": "1. **Titre** : contenu",
        "sources": "1. [INSEE](https://insee.fr)"
    }

    response = client.post("/download", data=payload)
    
    assert response.status_code == 200
    assert "markdown" in response.headers["Content-Type"]
    assert "Résultat de l’analyse DataScope".encode("utf-8") in response.data


