# movie/resolvers.py
import os
import sys

# permettre l'import de config/repository depuis la racine du projet
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import repository as repo


def movie_with_id(_, info, _id):
    return repo.get_movie_by_id(_id)


def actor_with_id(_, info, _id):
    return repo.get_actor_by_id(_id)


def update_movie_rate(_, info, _id, _rate):
    return repo.update_movie_rating(_id, _rate)


def add_actor_to_movie(_, info, _id, movie_id):
    # ici _id = id de l'acteur, movie_id = id du film
    return repo.add_movie_to_actor(_id, movie_id)


def update_movie(_, info, _id, _title, _director, _rate):
    return repo.update_movie_full(_id, _title, _director, _rate)


def create_movie(_, info, _id, _title, _director, _rate):
    return repo.create_movie(_id, _title, _director, _rate)


def delete_movie(_, info, _id):
    return repo.delete_movie(_id)


def create_actor(_, info, _id, _firstname, _lastname, _birthyear):
    return repo.create_actor(_id, _firstname, _lastname, _birthyear)


def delete_actor(_, info, _id):
    return repo.delete_actor(_id)


def resolve_actors_in_movie(movie, info):
    # movie est déjà un dict avec au moins movie["id"]
    return repo.get_actors_for_movie(movie["id"])
