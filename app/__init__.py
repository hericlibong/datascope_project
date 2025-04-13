from flask import Flask
from dotenv import load_dotenv
import os


def create_app():
    # Charge les variables d'environnement
    load_dotenv()

    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-key")

    # Enregistre les routes
    from app.routes import main
    app.register_blueprint(main)

    return app
