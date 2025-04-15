# Étape 1 : Image de base légère avec Python 3.12.3-slim-bullseye
FROM python:3.12-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt ./

# Installer les dépendances
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copier tout le reste de l’application dans le conteneur
COPY . .

# Définir la variable d'environnement pour Flask
ENV FLASK_APP=main.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

# Port par défaut pour Render
EXPOSE 5000

# Commande de démarrage
# CMD ["python", "main.py"]
# CMD ["sh", "-c", "flask run --host=0.0.0.0 --port=${PORT}"]
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]




