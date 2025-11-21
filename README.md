# S5-AD-GraphQL-TP2-MIXTE – REST + GraphQL + gRPC

---

<p style="text-align: center">
  <a href="https://www.daner-sharifi.com">
    <img src="https://img.shields.io/badge/Daner%20SHARIFI-FIL A1-blue?style=for-the-badge" alt="Daner SHARIFI">
  </a>
  <a href="mailto:bastien.bouvet@imt-atlantique.net">
    <img src="https://img.shields.io/badge/Bastien%20BOUVET-FIL A1-blueviolet?style=for-the-badge" alt="Bastien BOUVET">
  </a>
</p>

<p style="text-align: center">
  <img src="https://img.shields.io/badge/Python-3.10+-informational?style=flat-square"  alt="Python 3.10+"/>
  <img src="https://img.shields.io/badge/Flask-REST-success?style=flat-square" alt="Flask REST"/>
  <img src="https://img.shields.io/badge/Ariadne-GraphQL-orange?style=flat-square" alt="Ariadne GraphQL"/>
  <img src="https://img.shields.io/badge/gRPC-Microservices-brightgreen?style=flat-square" alt="gRPC Microservices"/>
  <img src="https://img.shields.io/badge/MongoDB-JSON%20↔%20DB-darkgreen?style=flat-square" alt="MongoDB JSON to DB"/>
  <img src="https://img.shields.io/badge/Docker-Multi--services-blue?style=flat-square" alt="Docker Multi-services"/>
</p>

---

Ce TP prolonge le TP REST avec une architecture **MIXTE** :

* **User** → API **REST** (Flask)
* **Movie** → API **GraphQL** (Ariadne)
* **Schedule** → service **gRPC** (Times)
* **Booking** → API **GraphQL** (Ariadne)

Objectifs :

* manipuler **3 styles d’API** (REST, GraphQL, gRPC) dans la même appli,

* pouvoir basculer entre **JSON fichiers** et **MongoDB** avec une simple variable (`USE_MONGO`),

* supporter 4 scénarios d’exécution :

    1. App non conteneurisée + JSON
    2. App non conteneurisée + Mongo conteneurisé
    3. App conteneurisée + JSON
    4. App conteneurisée + Mongo conteneurisé

* gérer les appels inter-services :

    * Booking → User (REST)
    * Schedule → Movie (GraphQL)
    * Booking → Schedule (gRPC)

---

## 1. Installation du projet

### 1.1. Cloner le dépôt

```bash
git clone https://github.com/DanerSharifi-FR/S5-AD-GraphQL-TP2-MIXTE.git
cd S5-AD-GraphQL-TP2-MIXTE
```

### 1.2. Créer l’environnement Python

Prérequis :

* Python **3.10+**
* `pip`
* (optionnel) `virtualenv` ou `python -m venv`

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

---

## 2. Configuration ( `.env` + Docker )

Toute la config passe par :

* **`.env`** à la racine (hors Docker),
* **`config.py`** qui lit les variables,
* `docker-compose.yml` qui injecte des variables spécifiques pour les containers.

### 2.1. Idées importantes pour `.env` :

* **Mongo**
    * activation via `USE_MONGO` (`1` pour Mongo, `0` pour JSON fichiers)
    * hors Docker : `MONGO_URI=mongodb://localhost`
    * en Docker : `MONGO_URI_DOCKER=mongodb://mongo-mixte`
* **Ports** séparés (utilisés par Flask/gRPC) : `*_PORT`
* **Services hors Docker** :

    * REST/GraphQL → `http://localhost` + port dans le code (`:MOVIE_PORT`, etc.)
    * gRPC Schedule → `SCHEDULE_SERVICE_URL=localhost` + port dans le code (`:SCHEDULE_PORT`), **sans** `http://`.

### 2.2. Rôle de `config.py` (logique générale)

`config.py` fait essentiellement :

* charge `.env` (via `python-dotenv` si dispo),
* expose des constantes .env en Python (`USE_MONGO`, `MONGO_URI`, etc.),

### 2.3. Variables en Docker (`docker-compose.yml`)

En Docker, on injecte des valeurs adaptées au réseau Docker :

* host pour User : `http://user-mixte`
* host pour Movie : `http://movie-mixte`
* host gRPC Schedule : `schedule-mixte`
* les ports sont ajoutés dans le code.

Ces valeurs sont injectées via `environment:` dans chaque service du `docker-compose.yml` et elles sont d'origine dans `.env`.

---

## 3. Documentation API (REST + GraphQL + gRPC)

### 3.1. Service User (REST – Flask)

**Port** : `USER_PORT` (`3203`)

| Méthode | URL                      | Description                            |
|--------:|--------------------------|----------------------------------------|
|     GET | `/`                      | Message de bienvenue                   |
|     GET | `/json`                  | Liste brute de tous les utilisateurs   |
|     GET | `/users/{userid}`        | Récupérer un utilisateur par id        |
|     GET | `/usersbyname?name=...`  | Récupérer un utilisateur par nom exact |
|    POST | `/users/{userid}`        | Créer un utilisateur avec cet id       |
|     PUT | `/users/{userid}/{last}` | Mettre à jour `last_active`            |
|  DELETE | `/users/{userid}`        | Supprimer un utilisateur               |

Stockage : `user/databases/users.json` ou collection Mongo `users` (base `cinema_mixte`) selon `USE_MONGO`.

---

### 3.2. Service Movie (GraphQL – Ariadne)

**Port** : `MOVIE_PORT` (`3200`)
**Endpoint** : `POST /graphql`

Schéma disponible dans `movie/movie.graphql`.
Voici les opérations principales :

| Opération                 | Description                            |
|---------------------------|----------------------------------------|
| `movie_with_id(_id)`      | Récupérer un film par id               |
| `actor_with_id(_id)`      | Récupérer un acteur par id             |
| `update_movie_rate(...)`  | Mettre à jour la note d’un film        |
| `update_movie(...)`       | Mettre à jour les infos d’un film      |
| `create_movie(...)`       | Créer un nouveau film                  |
| `delete_movie(_id)`       | Supprimer un film par id               |
| `create_actor(...)`       | Créer un nouvel acteur                 |
| `delete_actor(_id)`       | Supprimer un acteur par id             |
| `add_actor_to_movie(...)` | Ajouter un acteur à la liste d’un film |

Stockage : `movie/data/movies.json`, `movie/data/actors.json` ou Mongo, suivant la manière dont tu as branché
`repository`.

---

### 3.3. Service Schedule (gRPC – Times)

**Port gRPC** : `SCHEDULE_PORT` (`3202`)
**Pas d’endpoint HTTP** : uniquement gRPC.

Proto (`schedule/protos/times.proto`) des opérations gRPC :

| Méthode             | Description                                |
|---------------------|--------------------------------------------|
| `GetScheduleByDate` | Récupérer la programmation d’un jour donné |
| `AddSchedule`       | Ajouter une programmation pour un jour     |
| `DeleteSchedule`    | Supprimer la programmation d’un jour donné |

Logique :
* `GetScheduleByDate(date)` → lit via `schedule/repository.py`
* `DeleteSchedule(date)` → supprime via repo
* `AddSchedule` appelle Movie GraphQL (`MOVIE_SERVICE_URL` + `:MOVIE_PORT/graphql`)
* données : `schedule/data/times.json` ou Mongo (si repo branché).

---

### 3.4. Service Booking (GraphQL – Ariadne)

**Port** : `BOOKING_PORT` (`3201`)
**Endpoint** : `POST /graphql`

Schéma (`booking/booking.graphql`) des opérations GraphQL :

| Opération                 | Description                                 |
|---------------------------|---------------------------------------------|
| `booking_by_user(userid)` | Récupérer la réservation d’un utilisateur   |
| `add_booking(...)`        | Ajouter une réservation pour un utilisateur |
| `delete_booking(userid)`  | Supprimer la réservation d’un utilisateur   |


Logique :

* `booking_by_user(userid)` → lit via `booking/repository.py`
* `add_booking(userid, dates)` :

    * vérifie que l’utilisateur existe (`USER_SERVICE_URL` + `:USER_PORT/users/{id}`)
    * pour chaque date :

        * appelle gRPC Schedule (`SCHEDULE_SERVICE_URL` + `:SCHEDULE_PORT`) → `GetScheduleByDate`
        * vérifie que tous les films de la réservation sont bien programmés ce jour-là
    * crée la réservation (JSON ou Mongo)
* `delete_booking(userid)` → supprime via repo

Stockage : `booking/databases/bookings.json` ou collection Mongo `bookings`.

---

## 4. Lancer les 4 cas

On combine 2 axes :

* **Stockage** : JSON vs MongoDB (`USE_MONGO`)
* **Déploiement** : local Python vs Docker

---

### Cas 1 – App non conteneurisée + JSON

**But** : tout en Python local, fichiers JSON seulement.

1. `.env` :

   ```env
   USE_MONGO=0
   ```

2. Ne lance **pas** de Mongo.

3. Lancer les services (dans des terminaux séparés ou en fond) :

   ```bash
   source .venv/bin/activate

   python user/user.py
   python movie/movie.py
   python schedule/schedule.py
   python booking/booking.py
   ```

4. Tests rapides :

    * User REST : `GET http://localhost:3203/users/<id>`
    * Movie GraphQL : `POST http://localhost:3200/graphql`
    * Booking GraphQL : `POST http://localhost:3201/graphql`
    * Schedule : via client gRPC (`localhost:3202`)

---

### Cas 2 – App non conteneurisée + Mongo conteneurisé

**But** : services Python en local, Mongo dans Docker.

1. `.env` :

   ```env
   USE_MONGO=1
   MONGO_URI=mongodb://localhost
   MONGO_DB_NAME=cinema_mixte
   ```

2. Lancer Mongo :

   ```bash
   docker compose up mongo
   ```

3. Importer les données JSON → Mongo (si tu as `import_json_into_mongo.py` adapté) :

   ```bash
   source .venv/bin/activate
   python import_json_into_mongo.py
   ```

4. Lancer les services Python comme dans le cas 1 :

   ```bash
   python user/user.py
   python movie/movie.py
   python schedule/schedule.py
   python booking/booking.py
   ```

Les `repository.py` détectent `USE_MONGO=1` et basculent sur Mongo.

---

### Cas 3 – App conteneurisée + JSON

**But** : tout en Docker, mais les services utilisent toujours les fichiers JSON.

1. `.env` :

   ```env
   USE_MONGO=0
   ```

2. Lancer la stack :

   ```bash
   docker compose up user movie schedule booking
   ```

3. Les services tournent dans :

    * `user-mixte` (REST),
    * `movie-mixte` (GraphQL),
    * `schedule-mixte` (gRPC),
    * `booking-mixte` (GraphQL),

   avec des volumes :

    * `./user/databases → /app/user/databases`
    * `./movie/data → /app/movie/data`
    * `./schedule/data → /app/schedule/data`
    * `./booking/databases → /app/booking/databases`

Le container Mongo tourne éventuellement, mais n’est pas utilisé (`USE_MONGO=0`).

---

### Cas 4 – App conteneurisée + Mongo conteneurisé

**But** : stack complète microservices + base Mongo, tout en Docker.

1. `.env` :

   ```env
   USE_MONGO=1
   ```

2. Lancer Mongo + services :

   ```bash
   docker compose up mongo user movie schedule booking
   ```

3. Importer les données dans Mongo **depuis ta machine hôte** (qui voit Mongo sur `localhost:27017`) :

   ```bash
   source .venv/bin/activate
   python import_json_into_mongo.py
   ```

4. Tous les services dans Docker utiliseront alors Mongo (`USE_MONGO=1`) via `MONGO_URI_DOCKER`.