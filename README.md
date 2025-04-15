# 🧠 Datascope

[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Flask](https://img.shields.io/badge/flask-2.x-lightgrey)](https://flask.palletsprojects.com/)
[![Deployment](https://img.shields.io/badge/deployed-Render-success)](https://datascope.onrender.com/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## A tool to reveal the data potential of journalistic articles

**DataScope** is a Flask-based application designed to help journalists identify the “data” potential in a given article. It combines NLP and AI to extract key entities, compute a datafication score, suggest editorial angles, and propose relevant open data sources.

🔗 **Live app**: [https://datascope.onrender.com/](https://datascope.onrender.com/)

---

## 🔍 Objective

Build a lightweight assistant that:
- Detects key entities, numbers, locations, dates (via local NLP)
- Calculates a “datafication” score
- Generates AI-powered editorial angles (via LLM)
- Suggests open data sources or APIs to explore
- Allows export of the analysis (Markdown, JSON)

> ⚠️ NLP is currently optimized for **French** (using spaCy `fr_core_news_sm`). Support for other languages could be added later.

---

## 🚀 Tech Stack

- **Python 3.12**
- **Flask** for the web interface
- **spaCy** for local NLP processing
- **OpenAI API** for editorial suggestions
- **pdfminer / python-docx** for multi-format input
- **pytest** and `black` for testing and code formatting

---

## 🧩 Project Structure

```
├── app/         # Flask app (routes, views)
├── core/        # Core processing modules (parsing, NLP, LLM)
├── templates/   # Jinja2 HTML templates
├── static/      # CSS, images
├── tests/       # Test files
├── .env.sample  # Sample environment config
├── requirements.txt
├── README.md
└── run.py       # Entry point
```

---

## 🗂️ MVP Roadmap

- ✅ Project initialization
- ✅ Basic NLP analysis
- ✅ Editorial angle generation (LLM)
- ✅ Flask UI and result display
- ✅ Markdown / JSON export
- ✅ Dockerization and deployment (Render)


---

## 📷 Aperçu de l’interface (optionnel)

![interface home](medias/datascope_1.png)

---


## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
