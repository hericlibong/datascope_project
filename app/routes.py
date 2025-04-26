from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from core.article_parser import extract_article_text
from core.nlp_utils import format_entities, compute_datafication_score
from core.llm_engine import generate_journalistic_angles, suggest_datasets_llm, parse_markdown_list
import os
from werkzeug.utils import secure_filename
from core.nlp_utils import group_named_entities
from core.nlp_utils import interpret_datafication_score
from core.nlp_utils import get_article_profile
from flask import send_file
from core.export_utils import export_analysis_to_markdown
from langdetect import detect, LangDetectException
import tempfile
from datetime import datetime
from flask_login import login_user, logout_user, login_required
from models import get_user_by_email, USERS

main = Blueprint("main", __name__)


UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"txt", "pdf", "docx"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route("/", methods=["GET"])
def home():
    language = session.get("lang", "fr")
    return render_template("analyze.html", language=language)

@main.route("/login", methods=["GET", "POST"])
def login():
    language = session.get("lang", "en")
    if request.method == "POST":
        email = request.form.get("email")
        email = email.strip().lower()   # ✅ nettoyage indispensable ici aussi
        user = get_user_by_email(email)
        if user:
            login_user(user)
            return redirect(url_for("main.home"))
        else:
            message = {
                "fr": "Problème d'identification.",
                "en": "Authentication problem."
            }
            return render_template("login.html", error=message[language], language=language)
    return render_template("login.html", language=language)


@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.login"))



@main.route("/analyze", methods=["POST"])
@login_required
def analyze():
    article_text = ""

    language = session.get("lang", "en")

    # Si texte collé manuellement
    if request.form.get("article_text"):
        article_text = request.form.get("article_text")

    # Si fichier téléversé
    elif "article_file" in request.files:
        file = request.files["article_file"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(UPLOAD_FOLDER, filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            file.save(path)
            article_text = extract_article_text(path)

        # Vérification de la taille du texte
    word_count = len(article_text.strip().split())

    if word_count <= 200:
        message = {
            "fr": "Le texte est trop court pour une analyse pertinente. Veuillez fournir au moins 201 mots.",
            "en": "The text is too short for meaningful analysis. Please provide at least 201 words."
        }
        return render_template("analyze.html", error=message[language], language=language)

    if word_count > 3000:
        message = {
            "fr": "Le texte est trop long. La version actuelle accepte jusqu'à 3000 mots.",
            "en": "The text is too long. The current version accepts up to 3000 words."
        }
        return render_template("analyze.html", error=message[language], language=language)



    # Traitement uniquement si texte trouvé
    # Vérification de la langue du texte
    if article_text.strip():
        try:
            detected_lang = detect(article_text)
        except LangDetectException:
            detected_lang = "unknown"

        # Si la langue détectée ne correspond pas à celle sélectionnée
        lang_map = {"fr": "fr", "en": "en"}
        if detected_lang not in lang_map or lang_map[detected_lang] != language:
            message = {
                "fr": "Le texte semble être dans une autre langue que celle sélectionnée. Veuillez vérifier.",
                "en": "The text appears to be in a different language than the one selected. Please check."
            }
            return render_template("analyze.html", error=message[language], language=language)

        entities = format_entities(article_text, language)
        score_data = compute_datafication_score(entities, article_text)
        angles = generate_journalistic_angles(article_text, language)
        sources = suggest_datasets_llm(article_text, entities, language)
        parsed_angles = parse_markdown_list(angles)
        parsed_sources = parse_markdown_list(sources)
        grouped_entities = group_named_entities(entities["named_entities"])
        score_comment = interpret_datafication_score(score_data["score"], language)
        profile_label = get_article_profile(entities, score_data, language)

        return render_template(
            "results.html",
            article_text=article_text,
            entities=entities,
            grouped_entities=grouped_entities,
            score=score_data,
            score_comment=score_comment,
            profile_label=profile_label,
            angles=angles,
            sources=sources,
            parsed_angles=parsed_angles,
            parsed_sources=parsed_sources,
            language=language,
        )

    return render_template("analyze.html", error="Aucun texte ou fichier valide fourni.", language=language)


@main.route("/download", methods=["POST"])
def download():
    article_text = request.form.get("article_text")
    score = eval(request.form.get("score"))  # ou json.loads(...) si tu préfères
    score_comment = request.form.get("score_comment")
    profile = request.form.get("profile")
    entities = eval(request.form.get("entities"))
    angles = request.form.get("angles")
    sources = request.form.get("sources")
    language = session.get("lang", "fr")

    markdown = export_analysis_to_markdown(article_text, score, score_comment, profile, entities, angles, sources, language)

    # Créer un fichier temporaire
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".md", mode="w", encoding="utf-8")
    temp.write(markdown)
    temp.close()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    filename = f"datascope_{timestamp}.md"
    return send_file(temp.name, as_attachment=True, download_name=filename)


@main.route("/about", methods=["GET"])
def about():
    language = session.get("lang", "fr")
    return render_template("about.html", language=language)


@main.route("/set-language/<lang_code>")
def set_language(lang_code):
    if lang_code in ["fr", "en"]:
        session["lang"] = lang_code

    referrer = request.referrer or url_for("main.home")

    # Cas spécial : ne pas rediriger vers une page POST-only
    if referrer.endswith("/analyze"):
        language = session.get("lang", "fr")
        if language == "en":
            flash("The language has been updated. Please re-run the analysis to see results in English.")
        else:
            flash("La langue a bien été mise à jour. Veuillez relancer l’analyse pour afficher les résultats en français.")
        return redirect(url_for("main.home"))

    return redirect(referrer)
