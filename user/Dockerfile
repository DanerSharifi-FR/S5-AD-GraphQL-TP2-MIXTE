# image plus légère que "python"
FROM python:3.10-slim

# On bosse depuis /app (où il y aura tout le projet)
WORKDIR /app

# Copier les dépendances depuis la racine du projet
# (on va build avec context = .)
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier config.py dans l'image
COPY config.py .
COPY .env .
COPY ./user ./user

WORKDIR /app/user

EXPOSE 3203

# Démarrage du service user
CMD ["python", "user.py"]