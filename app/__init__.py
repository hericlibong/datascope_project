import markdown
from flask import Flask
from markupsafe import Markup
from dotenv import load_dotenv
from flask_login import LoginManager
from models import get_user_by_email, USERS
import os


def create_app():
    # Charge les variables d'environnement
    load_dotenv()

    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-key")

    # Enregistre les routes
    from app.routes import main
    app.register_blueprint(main)

    # Activer le filtre Markdown
    @app.template_filter('markdown')
    def markdown_filter(text):
        return Markup(markdown.markdown(text, extensions=['fenced_code']))

    login_manager = LoginManager()
    login_manager.login_view = "main.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        """
        Charge l'utilisateur à partir de l'ID.
        """
        for user in USERS.values():
            if user.id == user_id:
                return user
        return None

    return app
