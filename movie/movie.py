from ariadne import graphql_sync, make_executable_schema, load_schema_from_path, ObjectType, QueryType, MutationType
from flask import Flask, request, jsonify, make_response
import os
import sys

# allow imports from project root (config, etc.)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import resolvers as r
from config import HOST, MOVIE_PORT

app = Flask(__name__)
PORT = int(MOVIE_PORT)

# Chargement du schéma GraphQL avec un chemin robuste
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "movie.graphql")
type_defs = load_schema_from_path(SCHEMA_PATH)

query = QueryType()
mutation = MutationType()
movie = ObjectType("Movie")
actor = ObjectType("Actor")

# Query fields
query.set_field("movie_with_id", r.movie_with_id)
query.set_field("actor_with_id", r.actor_with_id)

# Movie fields
movie.set_field("actors", r.resolve_actors_in_movie)

# Mutations
mutation.set_field("update_movie_rate", r.update_movie_rate)
mutation.set_field("update_movie", r.update_movie)
mutation.set_field("create_movie", r.create_movie)
mutation.set_field("delete_movie", r.delete_movie)
mutation.set_field("create_actor", r.create_actor)
mutation.set_field("delete_actor", r.delete_actor)
mutation.set_field("add_actor_to_movie", r.add_actor_to_movie)

schema = make_executable_schema(type_defs, movie, query, mutation, actor)


# root message
@app.route("/", methods=["GET"])
def home():
    return make_response("<h1 style='color:blue'>Welcome to the Movie service!</h1>", 200)


# graphql entry point
@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value=None,
        debug=app.debug,
    )
    status_code = 200 if success else 400
    return jsonify(result), status_code


if __name__ == "__main__":
    print(f"Server running in port {PORT}")
    app.run(host=HOST, port=PORT)
