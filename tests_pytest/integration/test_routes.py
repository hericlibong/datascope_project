import pytest
from app import create_app  # ou directement depuis main.py si pas factorisé
import io


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.test_client() as client:
        # Simuler une session utilisateur pour bypass login_required
        with client.session_transaction() as session:
            session["_user_id"] = "1"  # L'ID d'un utilisateur fictif existant
        yield client


def test_login_get_page(client):
    """
    Teste l'affichage du formulaire de connexion (GET).
    """
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Email" in response.data or b"email" in response.data


def test_login_post_valid_email(client):
    """
    Teste un login réussi avec un email existant.
    """
    # Attention : ici il faut que l'email existe dans users.json
    response = client.post("/login", data={"email": "hericlibong@gmail.com"})
    assert response.status_code == 302  # Redirige vers home
    assert "/home" not in response.location  # peut être simplement "/"


def test_homepage_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Analyser un article" in response.data or b"form" in response.data


def test_analyze_route_with_text(client):
    # Générer un texte suffisamment long (> 200 mots)
    long_article = "In 2023, the UK government announced a major investment plan into offshore wind farms. " * 50
    payload = {"article_text": long_article}
    response = client.post("/analyze", data=payload)
    assert response.status_code == 200
    assert b"Datafication Score" in response.data


def test_about_page_loads(client):
    response = client.get("/about")
    assert response.status_code == 200
    assert b"A propos" in response.data or b"DataScope" in response.data


def test_analyze_with_uploaded_txt_file(client):
    text = ("On 3 April, 45 injured in Lyon in an earthquake. " * 50)  # Assez long > 200 mots
    data = {
        "article_file": (io.BytesIO(text.encode("utf-8")), "test_article.txt")
    }
    response = client.post("/analyze", data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert b"Datafication Score" in response.data


def test_analyze_route_with_empty_text(client):
    response = client.post("/analyze", data={"article_text": ""})
    assert response.status_code == 200
    assert b"Please provide at least 201 words" in response.data or b"Veuillez fournir au moins 201 mots" in response.data


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
