# image plus légère que "python"
FROM python:3.10-slim

# On bosse depuis /app (tout le projet)
WORKDIR /app

# Copier les dépendances depuis la racine du projet
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier **tout** le projet (config.py, schedule/, movie/, etc.)
COPY . .

# Aller dans le dossier schedule pour lancer le service gRPC
WORKDIR /app/schedule

# Info uniquement : le vrai port est SCHEDULE_PORT (config), par défaut 3202
EXPOSE 3202

# Démarrage du service gRPC schedule
CMD ["python", "schedule.py"]