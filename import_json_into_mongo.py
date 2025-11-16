import os
import json
from pymongo import MongoClient


def load_json_array(file_path: str, table_name: str) -> list:
    """
    Charge un tableau (liste) depuis un fichier JSON connu.

    On suppose que la structure du fichier est de la forme :

        {
          "<table_name>": [ ... ]
        }

    Exemple : pour users.json, on a :

        {
          "users": [ { ... }, { ... } ]
        }

    Paramètres
    ----------
    file_path : str
        Chemin complet du fichier JSON à lire.
    table_name : str
        Nom de la clé qui contient la liste (par exemple "users",
        "movies", "schedule", "bookings").

    Retour
    ------
    list
        La liste contenue sous cette clé. Si le fichier n'existe pas,
        est invalide ou ne contient pas la clé attendue, on renvoie
        une liste vide [] et on affiche un message d'avertissement.
    """
    if not os.path.exists(file_path):
        print(f"[seed] WARN: fichier introuvable : {file_path}")
        return []

    with open(file_path, "r", encoding="utf-8") as json_file:
        try:
            json_data = json.load(json_file)
        except json.JSONDecodeError:
            print(f"[seed] WARN: JSON invalide : {file_path}")
            return []

    if not isinstance(json_data, dict):
        print(f"[seed] WARN: structure inattendue (pas un dict) dans : {file_path}")
        return []

    array_value = json_data.get(table_name)
    if not isinstance(array_value, list):
        print(
            f"[seed] WARN: la clé '{table_name}' est absente ou ne "
            f"contient pas une liste dans : {file_path}"
        )
        return []

    return array_value


def main() -> None:
    # Dossier racine du projet (là où se trouve ce script)
    project_root_path = os.path.dirname(os.path.abspath(__file__))

    # Paramètres de connexion MongoDB
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    mongo_database_name = os.getenv("MONGO_DB_NAME", "cinema_mixte")

    print(f"[seed] Connexion à MongoDB : {mongo_uri}, base = {mongo_database_name}")
    mongo_client = MongoClient(mongo_uri)
    mongo_database = mongo_client[mongo_database_name]

    # Chemins vers les fichiers JSON du projet REST
    users_json_path = os.path.join(project_root_path, "user", "databases", "users.json")
    movies_json_path = os.path.join(project_root_path, "movie", "databases", "movies.json")
    actors_json_path = os.path.join(project_root_path, "movie", "databases", "actors.json")
    times_json_path = os.path.join(project_root_path, "schedule", "databases", "times.json")
    bookings_json_path = os.path.join(project_root_path, "booking", "databases", "bookings.json")

    # On connaît la structure de chaque fichier :
    # - users.json    -> clé "users"
    # - movies.json   -> clé "movies"
    # - times.json    -> clé "schedule"
    # - bookings.json -> clé "bookings"
    users_list = load_json_array(users_json_path, table_name="users")
    movies_list = load_json_array(movies_json_path, table_name="movies")
    actors_list = load_json_array(actors_json_path, table_name="actors")
    times_list = load_json_array(times_json_path, table_name="schedule")
    bookings_list = load_json_array(bookings_json_path, table_name="bookings")

    print(
        f"[seed] Données chargées depuis les JSON : "
        f"users={len(users_list)}, movies={len(movies_list)}, "
        f"actors={len(actors_list)}, "
        f"schedule={len(times_list)}, bookings={len(bookings_list)}"
    )

    # On vide puis on insère dans chaque collection MongoDB
    if users_list:
        mongo_database.users.delete_many({})
        mongo_database.users.insert_many(users_list)
        print(f"[seed] {len(users_list)} utilisateurs insérés dans 'users'")

    if movies_list:
        mongo_database.movies.delete_many({})
        mongo_database.movies.insert_many(movies_list)
        print(f"[seed] {len(movies_list)} films insérés dans 'movies'")

    if actors_list:
        mongo_database.actors.delete_many({})
        mongo_database.actors.insert_many(actors_list)
        print(f"[seed] {len(actors_list)} acteurs insérés dans 'actors'")

    if times_list:
        mongo_database.times.delete_many({})
        mongo_database.times.insert_many(times_list)
        print(f"[seed] {len(times_list)} horaires insérés dans 'times'")

    if bookings_list:
        mongo_database.bookings.delete_many({})
        mongo_database.bookings.insert_many(bookings_list)
        print(f"[seed] {len(bookings_list)} réservations insérées dans 'bookings'")

    print("[seed] Terminé.")


if __name__ == "__main__":
    main()
