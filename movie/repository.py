# movie/repository.py
import os
import json

from pymongo import MongoClient

from config import USE_MONGO, MONGO_URI, MONGO_DB_NAME

# Chemins vers les JSON locaux
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MOVIES_JSON_PATH = os.path.join(SCRIPT_DIR, "databases", "movies.json")
ACTORS_JSON_PATH = os.path.join(SCRIPT_DIR, "databases", "actors.json")

_client = None
_db = None
_movies_col = None
_actors_col = None

if USE_MONGO:
    _client = MongoClient(MONGO_URI)
    _db = _client[MONGO_DB_NAME]
    _movies_col = _db["movies"]
    _actors_col = _db["actors"]


# -------------------------
# Helpers JSON
# -------------------------

def _load_json_movies():
    if not os.path.exists(MOVIES_JSON_PATH):
        return []

    with open(MOVIES_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        return data.get("movies", [])
    return data


def _write_json_movies(movies_list):
    os.makedirs(os.path.dirname(MOVIES_JSON_PATH), exist_ok=True)
    with open(MOVIES_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump({"movies": movies_list}, f, ensure_ascii=False, indent=2)


def _load_json_actors():
    if not os.path.exists(ACTORS_JSON_PATH):
        return []

    with open(ACTORS_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        return data.get("actors", [])
    return data


def _write_json_actors(actors_list):
    os.makedirs(os.path.dirname(ACTORS_JSON_PATH), exist_ok=True)
    with open(ACTORS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump({"actors": actors_list}, f, ensure_ascii=False, indent=2)


# -------------------------
# Movies
# -------------------------

def get_movie_by_id(movie_id: str):
    if USE_MONGO and _movies_col is not None:
        return _movies_col.find_one({"id": str(movie_id)}, {"_id": 0})

    for movie in _load_json_movies():
        if str(movie.get("id")) == str(movie_id):
            return movie
    return None


def get_movie_by_title(title: str):
    if USE_MONGO and _movies_col is not None:
        return _movies_col.find_one({"title": title}, {"_id": 0})

    for movie in _load_json_movies():
        if str(movie.get("title")) == str(title):
            return movie
    return None


def update_movie_rating(movie_id: str, rate: float):
    if USE_MONGO and _movies_col is not None:
        res = _movies_col.update_one(
            {"id": str(movie_id)},
            {"$set": {"rating": float(rate)}},
        )
        if res.matched_count == 0:
            return None
        return _movies_col.find_one({"id": str(movie_id)}, {"_id": 0})

    movies = _load_json_movies()
    updated_movie = None

    for m in movies:
        if str(m.get("id")) == str(movie_id):
            m["rating"] = float(rate)
            updated_movie = m
            break

    if updated_movie is not None:
        _write_json_movies(movies)

    return updated_movie


def update_movie_full(movie_id: str, title: str, director: str, rate: float):
    if USE_MONGO and _movies_col is not None:
        res = _movies_col.update_one(
            {"id": str(movie_id)},
            {"$set": {
                "title": title,
                "director": director,
                "rating": float(rate),
            }},
        )
        if res.matched_count == 0:
            return None
        return _movies_col.find_one({"id": str(movie_id)}, {"_id": 0})

    movies = _load_json_movies()
    updated_movie = None

    for m in movies:
        if str(m.get("id")) == str(movie_id):
            m["title"] = title
            m["director"] = director
            m["rating"] = float(rate)
            updated_movie = m
            break

    if updated_movie is not None:
        _write_json_movies(movies)

    return updated_movie


def create_movie(movie_id: str, title: str, director: str, rate: float):
    new_movie = {
        "id": str(movie_id),
        "title": title,
        "director": director,
        "rating": float(rate),
    }

    if USE_MONGO and _movies_col is not None:
        if _movies_col.find_one({"id": new_movie["id"]}):
            return None
        _movies_col.insert_one(new_movie)
        return _movies_col.find_one({"id": new_movie["id"]}, {"_id": 0})

    movies = _load_json_movies()
    for m in movies:
        if str(m.get("id")) == new_movie["id"]:
            return None

    movies.append(new_movie)
    _write_json_movies(movies)
    return new_movie


def delete_movie(movie_id: str):
    if USE_MONGO and _movies_col is not None:
        deleted = _movies_col.find_one({"id": str(movie_id)}, {"_id": 0})
        if not deleted:
            return None
        _movies_col.delete_one({"id": str(movie_id)})
        return deleted

    movies = _load_json_movies()
    deleted_movie = None
    remaining = []

    for m in movies:
        if deleted_movie is None and str(m.get("id")) == str(movie_id):
            deleted_movie = m
        else:
            remaining.append(m)

    if deleted_movie is not None:
        _write_json_movies(remaining)

    return deleted_movie


# -------------------------
# Actors
# -------------------------

def get_actor_by_id(actor_id: str):
    if USE_MONGO and _actors_col is not None:
        return _actors_col.find_one({"id": str(actor_id)}, {"_id": 0})

    for actor in _load_json_actors():
        if str(actor.get("id")) == str(actor_id):
            return actor
    return None


def create_actor(actor_id: str, firstname: str, lastname: str, birthyear: int):
    new_actor = {
        "id": str(actor_id),
        "firstname": firstname,
        "lastname": lastname,
        "birthyear": int(birthyear),
        "films": [],
    }

    if USE_MONGO and _actors_col is not None:
        if _actors_col.find_one({"id": new_actor["id"]}):
            return None
        _actors_col.insert_one(new_actor)
        return _actors_col.find_one({"id": new_actor["id"]}, {"_id": 0})

    actors = _load_json_actors()
    for a in actors:
        if str(a.get("id")) == new_actor["id"]:
            return None

    actors.append(new_actor)
    _write_json_actors(actors)
    return new_actor


def delete_actor(actor_id: str):
    if USE_MONGO and _actors_col is not None:
        deleted = _actors_col.find_one({"id": str(actor_id)}, {"_id": 0})
        if not deleted:
            return None
        _actors_col.delete_one({"id": str(actor_id)})
        return deleted

    actors = _load_json_actors()
    deleted_actor = None
    remaining = []

    for a in actors:
        if deleted_actor is None and str(a.get("id")) == str(actor_id):
            deleted_actor = a
        else:
            remaining.append(a)

    if deleted_actor is not None:
        _write_json_actors(remaining)

    return deleted_actor


def add_movie_to_actor(actor_id: str, movie_id: str):
    if USE_MONGO and _actors_col is not None:
        # on évite les doublons avec $addToSet
        res = _actors_col.update_one(
            {"id": str(actor_id)},
            {"$addToSet": {"films": str(movie_id)}},
        )
        if res.matched_count == 0:
            return None
        return _actors_col.find_one({"id": str(actor_id)}, {"_id": 0})

    actors = _load_json_actors()
    updated_actor = None

    for a in actors:
        if str(a.get("id")) == str(actor_id):
            if "films" not in a or not isinstance(a["films"], list):
                a["films"] = []
            if str(movie_id) not in a["films"]:
                a["films"].append(str(movie_id))
            updated_actor = a
            break

    if updated_actor is not None:
        _write_json_actors(actors)

    return updated_actor


def get_actors_for_movie(movie_id: str):
    """
    Retourne la liste des acteurs qui ont ce film dans leur liste 'films'.
    """
    if USE_MONGO and _actors_col is not None:
        return list(
            _actors_col.find(
                {"films": str(movie_id)},
                {"_id": 0},
            )
        )

    actors = _load_json_actors()
    result = []
    for a in actors:
        films = a.get("films", [])
        if isinstance(films, list) and str(movie_id) in films:
            result.append(a)
    return result
