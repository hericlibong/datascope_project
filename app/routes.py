from flask import Blueprint, render_template, request
from core.article_parser import extract_article_text
from core.nlp_utils import format_entities, compute_datafication_score
from core.llm_engine import generate_journalistic_angles, suggest_datasets_llm
import os
from werkzeug.utils import secure_filename
from core.nlp_utils import group_named_entities


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
        entities = format_entities(article_text)
        score_data = compute_datafication_score(entities, article_text)
        angles = generate_journalistic_angles(article_text)
        sources = suggest_datasets_llm(article_text, entities)
        grouped_entities = group_named_entities(entities["named_entities"])

        return render_template(
            "results.html",
            article_text=article_text,
            entities=entities,
            grouped_entities=grouped_entities,
            score=score_data,
            angles=angles,
            sources=sources
)


    return render_template("analyze.html", error="Aucun texte ou fichier valide fourni.")
