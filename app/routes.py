from flask import Blueprint, render_template, request, session, redirect, url_for, flash, abort
from core.article_parser import extract_article_text
from core.nlp_utils import format_entities, compute_datafication_score
from core.llm_engine import generate_journalistic_angles, suggest_datasets_llm, parse_markdown_list, suggest_visualizations_llm
import os
import json
from werkzeug.utils import secure_filename
from core.nlp_utils import group_named_entities
from core.nlp_utils import interpret_datafication_score
from core.nlp_utils import get_article_profile
from flask import send_file
from core.export_utils import export_analysis_to_markdown
from langdetect import detect, LangDetectException
import tempfile
from datetime import datetime
from flask_login import login_user, logout_user, login_required, current_user
from models import get_user_by_email, USERS, ADMIN_EMAIL
from io import BytesIO
import re
import markdown

main = Blueprint("main", __name__)


UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"txt", "pdf", "docx"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@main.route("/admin/users")
@login_required
def admin_users():
    from models import ADMIN_EMAIL
    if not current_user.is_authenticated or current_user.email != ADMIN_EMAIL:
        abort(403)

    try:
        with open("users.json", "r") as f:
            users_data = json.load(f)
    except Exception:
        users_data = {}

    return render_template("admin_users.html", users=users_data, language=session.get("lang", "en"))


# 📩 Route pour afficher et enregistrer le feedback structuré
@main.route("/feedback", methods=["GET", "POST"])
@login_required
def feedback():
    language = session.get("lang", "en")

    if request.method == "POST":
        email = current_user.email

        # Données du formulaire
        relevance = request.form.get("relevance")
        angles = request.form.get("angles")
        sources = request.form.get("sources")
        reusability = request.form.get("reusability")
        message = request.form.get("message", "").strip()

        if relevance and angles and sources and reusability:
            try:
                with open("feedbacks.json", "r") as f:
                    feedbacks = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                feedbacks = {}

            timestamp = datetime.utcnow().isoformat(timespec='seconds')

            feedbacks[timestamp] = {
                "email": email,
                "relevance": relevance,
                "angles": angles,
                "sources": sources,
                "reusability": reusability,
                "message": message
            }

            with open("feedbacks.json", "w") as f:
                json.dump(feedbacks, f, indent=4, ensure_ascii=False)

            success_message = {
                "fr": "Merci pour votre retour structuré !",
                "en": "Thank you for your detailed feedback!"
            }

            return render_template("feedback.html", success=success_message[language], language=language)

    return render_template("feedback.html", language=language)


# 🔒 Route d'administration pour consulter les feedbacks
@main.route("/admin/feedbacks")
@login_required
def admin_feedbacks():
    # from models import ADMIN_EMAIL

    if current_user.email != ADMIN_EMAIL:
        abort(403)

    try:
        with open("feedbacks.json", "r") as f:
            feedbacks = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        feedbacks = {}

    return render_template("admin_feedbacks.html", feedbacks=feedbacks, language=session.get("lang", "en"))


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
    if article_text.strip():
        try:
            detected_lang = detect(article_text)
        except LangDetectException:
            detected_lang = "unknown"

        # Vérification de la langue détectée vs langue choisie
        lang_map = {"fr": "fr", "en": "en"}
        if detected_lang not in lang_map or lang_map[detected_lang] != language:
            message = {
                "fr": "Le texte semble être dans une autre langue que celle sélectionnée. Veuillez vérifier.",
                "en": "The text appears to be in a different language than the one selected. Please check."
            }
            return render_template("analyze.html", error=message[language], language=language)

        # Analyse NLP et LLM
        entities = format_entities(article_text, language)
        score_data = compute_datafication_score(entities, article_text)
        angles = generate_journalistic_angles(article_text, language)
        sources = suggest_datasets_llm(article_text, entities, language)
        parsed_angles = parse_markdown_list(angles)
        parsed_sources = parse_markdown_list(sources)
        grouped_entities = group_named_entities(entities["named_entities"])
        score_comment = interpret_datafication_score(score_data["score"], language)
        profile_label = get_article_profile(entities, score_data, language)

             
        # 🧮  Génération des suggestions de visualisation pour chaque angle
        try:
            viz_suggestions = suggest_visualizations_llm(parsed_angles, language)
            print("Réponse LLM Brute (Visualisation) :\n", viz_suggestions)

            # -------- 1. découper bloc par bloc ------------- #
            bloc_re = re.compile(
                r"^\d+\.\s+\*\*(.*?)\*\*\s*(.*?)(?=\n\d+\.\s|\Z)",
                re.DOTALL | re.MULTILINE
            )
            blocs = bloc_re.findall(viz_suggestions)

            for idx, angle in enumerate(parsed_angles):
                if idx < len(blocs):
                    _titre, corps = blocs[idx]

                    # -------- 2. extraire chaque puce ------------- #
                    items = []
                    for m in re.findall(r"^\s*-\s+\*\*(.*?)\*\*\s*:\s*(.*?)(?=\n\s*-\s|\Z)", 
                                        corps, re.DOTALL | re.MULTILINE):
                        viz_title, desc = m
                        # format Markdown propre : **Titre** : description
                        items.append(f"- **{viz_title.strip()}**: {desc.strip()}")

                    # Si pas de puce détectée, on garde le corps tel quel
                    markdown_in = "\n".join(items) if items else corps.strip()

                    # -------- 3. conversion Markdown -> HTML -------- #
                    angle["visualization"] = markdown.markdown(markdown_in)
                else:
                    angle["visualization"] = "<em>N/A</em>"
        except Exception as e:
            print("Erreur parsing visualisations :", e)
            for angle in parsed_angles:
                angle["visualization"] = "<em>N/A</em>"




        # Comptage des types d'entités
        entity_counts = {
            "Named Entities": len(entities.get("named_entities", [])),
            "Numbers + Units": len(entities.get("numbers", [])),
            "Dates": len(entities.get("dates", [])),
            "Strong Verbs": len(entities.get("strong_verbs", [])),
        }

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
            entity_counts=entity_counts,  # ✅ Nouvel élément
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


@main.route("/guide", methods=["GET"])
def guide():
    language = session.get("lang", "en")
    return render_template("guide.html", language=language)


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


@main.route("/admin/download-feedbacks")
@login_required
def download_feedbacks():
    if current_user.email != ADMIN_EMAIL:
        abort(403)

    try:
        with open("feedbacks.json", "rb") as f:
            content = f.read()
        return send_file(
            BytesIO(content),
            mimetype="application/json",
            as_attachment=True,
            download_name="feedbacks.json"
        )
    except FileNotFoundError:
        return "Fichier de feedback introuvable.", 404
