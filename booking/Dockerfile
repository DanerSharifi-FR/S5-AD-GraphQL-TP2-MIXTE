FROM python:3.10-slim

WORKDIR /app

# dépendances depuis la racine du projet
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# copier tout le projet (config.py, booking/, user/, schedule/, movie/, etc.)
COPY . .

# aller dans le dossier booking
WORKDIR /app/booking

# info : port réel = BOOKING_PORT (config), par défaut 3201
EXPOSE 3201

CMD ["python", "booking.py"]