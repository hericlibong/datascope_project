from flask import Blueprint, render_template, request, session, redirect, url_for
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
import tempfile


main = Blueprint("main", __name__)


UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"txt", "pdf", "docx"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@main.route("/", methods=["GET"])
def home():
    return render_template("analyze.html")


@main.route("/analyze", methods=["POST"])
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

    # Traitement uniquement si texte trouvé
    if article_text.strip():
        entities = format_entities(article_text, language)
        score_data = compute_datafication_score(entities, article_text, language)
        angles = generate_journalistic_angles(article_text, language)
        sources = suggest_datasets_llm(article_text, entities)
        parsed_angles = parse_markdown_list(angles)
        parsed_sources = parse_markdown_list(sources)
        grouped_entities = group_named_entities(entities["named_entities"])
        score_comment = interpret_datafication_score(score_data["score"])
        profile_label = get_article_profile(entities, score_data)

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

    return render_template("analyze.html", error="Aucun texte ou fichier valide fourni.")


@main.route("/download", methods=["POST"])
def download():
    article_text = request.form.get("article_text")
    score = eval(request.form.get("score"))  # ou json.loads(...) si tu préfères
    score_comment = request.form.get("score_comment")
    profile = request.form.get("profile")
    entities = eval(request.form.get("entities"))
    angles = request.form.get("angles")
    sources = request.form.get("sources")

    markdown = export_analysis_to_markdown(article_text, score, score_comment, profile, entities, angles, sources)

    # Créer un fichier temporaire
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".md", mode="w", encoding="utf-8")
    temp.write(markdown)
    temp.close()

    return send_file(temp.name, as_attachment=True, download_name="analyse_datascope.md")


@main.route("/about", methods=["GET"])
def about():
    return render_template("about.html")


@main.route("/set-language/<lang_code>")
def set_language(lang_code):
    if lang_code in ["fr", "en"]:
        session['lang'] = lang_code
    return redirect(request.referrer or url_for('main.index'))
