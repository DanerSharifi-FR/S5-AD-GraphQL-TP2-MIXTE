# image plus légère que "python"
FROM python:3.10-slim

# On bosse depuis /app (où il y aura tout le projet)
WORKDIR /app

# Copier les dépendances depuis la racine du projet
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier **tout** le projet dans l'image (config.py, movie/, user/, etc.)
COPY . .

# Aller dans le dossier movie pour lancer le service GraphQL
WORKDIR /app/movie

# Info uniquement, le vrai port utilisé vient de MOVIE_PORT dans config.py
EXPOSE 3200

# Démarrage du service movie (Ariadne + Flask)
CMD ["python", "movie.py"]