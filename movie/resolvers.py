import json

def movie_with_id(_,info,_id):
    with open('{}/data/movies.json'.format("."), "r") as file:
        movies = json.load(file)
        for movie in movies['movies']:
            if movie['id'] == _id:
                return movie

def actor_with_id(_,info,_id):
    with open('{}/data/actors.json'.format("."), "r") as file:
        actors = json.load(file)
        for actor in actors['actors']:
            if actor['id'] == _id:
                return actor

def update_movie_rate(_,info,_id,_rate):
    newmovies = {}
    newmovie = {}
    with open('{}/data/movies.json'.format("."), "r") as rfile:
        movies = json.load(rfile)
        for movie in movies['movies']:
            if movie['id'] == _id:
                movie['rating'] = _rate
                newmovie = movie
                newmovies = movies
    with open('{}/data/movies.json'.format("."), "w") as wfile:
        json.dump(newmovies, wfile)
    return newmovie

def add_actor_to_movie(_,info,_id,movie_id):
    newactors = {}
    newactor = {}
    with open('{}/data/actors.json'.format("."), "r") as rfile:
        actors = json.load(rfile)
        for actor in actors['actors']:
            if actor['id'] == _id:
                if movie_id not in actor['films']:
                    actor['films'].append(movie_id)
                newactor = actor
                newactors = actors
    with open('{}/data/actors.json'.format("."), "w") as wfile:
        json.dump(newactors, wfile)
    return newactor

def update_movie(_, info, _id, _title, _director, _rate):
    updated_movie = None
    with open('{}/data/movies.json'.format("."), "r") as rfile:
        movies = json.load(rfile)
        for movie in movies['movies']:
            if movie['id'] == _id:
                movie['title'] = _title
                movie['director'] = _director
                movie['rating'] = _rate
                updated_movie = movie
    with open('{}/data/movies.json'.format("."), "w") as wfile:
        json.dump(movies, wfile)
    return updated_movie

def create_movie(_, info, _id, _title, _director, _rate):
    with open('{}/data/movies.json'.format("."), "r") as rfile:
        movies = json.load(rfile)
        new_movie = {
            "id": _id,
            "title": _title,
            "director": _director,
            "rating": _rate
        }
        movies['movies'].append(new_movie)
    with open('{}/data/movies.json'.format("."), "w") as wfile:
        json.dump(movies, wfile)
    return new_movie

def delete_movie(_, info, _id):
    deleted_movie = None
    with open('{}/data/movies.json'.format("."), "r") as rfile:
        movies = json.load(rfile)
        for movie in movies['movies']:
            if movie['id'] == _id:
                deleted_movie = movie
        movies['movies'] = [movie for movie in movies['movies'] if movie['id'] != _id]
    with open('{}/data/movies.json'.format("."), "w") as wfile:
        json.dump(movies, wfile)
    return deleted_movie

def create_actor(_, info, _id, _firstname, _lastname, _birthyear):
    with open('{}/data/actors.json'.format("."), "r") as rfile:
        actors = json.load(rfile)
        new_actor = {
            "id": _id,
            "firstname": _firstname,
            "lastname": _lastname,
            "birthyear": _birthyear,
            "films": []
        }
        actors['actors'].append(new_actor)
    with open('{}/data/actors.json'.format("."), "w") as wfile:
        json.dump(actors, wfile)
    return new_actor

def delete_actor(_, info, _id):
    deleted_actor = None
    with open('{}/data/actors.json'.format("."), "r") as rfile:
        actors = json.load(rfile)
        for actor in actors['actors']:
            if actor['id'] == _id:
                deleted_actor = actor
        actors['actors'] = [actor for actor in actors['actors'] if actor['id'] != _id]
    with open('{}/data/actors.json'.format("."), "w") as wfile:
        json.dump(actors, wfile)
    return deleted_actor

def resolve_actors_in_movie(movie, info):
    with open('{}/data/actors.json'.format("."), "r") as file:
        actors = json.load(file)
        result = [actor for actor in actors['actors'] if movie['id'] in actor['films']]
        return result