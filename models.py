from flask_login import UserMixin
import json
import os


class User(UserMixin):
    def __init__(self, id, email, username):
        self.id = id
        self.email = email
        self.username = username


# Charger users.json (ou créer vide si inexistant)
if os.path.exists("users.json"):
    with open("users.json", "r") as f:
        raw_users = json.load(f)
else:
    raw_users = {}

USERS = {
    email: User(data["id"], email, data["username"])
    for email, data in raw_users.items()
}


def save_users_to_json():
    """Enregistre USERS dans users.json"""
    data = {
        email: {"id": user.id, "username": user.username}
        for email, user in USERS.items()
    }
    with open("users.json", "w") as f:
        json.dump(data, f, indent=2)


def generate_username_from_email(email):
    """Crée un username basique à partir de l'email"""
    username = email.split("@")[0]
    return username.replace(".", "_").replace("-", "_")


def get_user_by_email(email):
    """Cherche un utilisateur ou crée un nouveau"""
    email = email.strip().lower()
    user = USERS.get(email)

    if not user:
        new_id = str(len(USERS) + 1)
        username = generate_username_from_email(email)
        user = User(new_id, email, username)
        USERS[email] = user
        save_users_to_json()

    return user
