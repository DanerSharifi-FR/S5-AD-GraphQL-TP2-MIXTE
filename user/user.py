from flask import Flask, request, jsonify, make_response
from werkzeug.exceptions import NotFound
import os
import sys

# allow imports from project root (config, etc.)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from repository import (
    get_all_users,
    get_user_by_id,
    get_user_by_name,
    add_user,
    update_user_last_active,
    delete_user,
)
from config import USER_PORT, HOST

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return "<h1 style='color:blue'>Welcome to the User service!</h1>"


@app.route("/users/<userid>", methods=["GET"])
def get_user_byid(userid):
    user = get_user_by_id(userid)
    if user is None:
        return make_response(jsonify({"error": "user ID not found"}), 500)
    return make_response(jsonify(user), 200)


@app.route("/json", methods=["GET"])
def get_json():
    users = get_all_users()
    return make_response(jsonify(users), 200)


# Read by name
@app.route("/usersbyname", methods=["GET"])
def get_user_by_name_route():
    if not request.args or "name" not in request.args:
        return make_response(jsonify({"error": "missing 'name' query param"}), 400)

    name = request.args["name"]
    user = get_user_by_name(name)

    if not user:
        return make_response(jsonify({"error": "user name not found"}), 500)

    return make_response(jsonify(user), 200)


# Create
@app.route("/users/<userid>", methods=["POST"])
def add_user_route(userid):
    req = request.get_json() or {}

    # Optionnel : forcer cohérence body/path
    if str(req.get("id")) != str(userid):
        req["id"] = str(userid)

    created = add_user(req)
    if created is None:
        return make_response(jsonify({"error": "user ID already exists"}), 500)

    return make_response(jsonify({"message": "user added"}), 200)


# Update
@app.route("/users/<userid>/<last_active>", methods=["PUT"])
def update_user_last_active_route(userid, last_active):
    updated = update_user_last_active(userid, last_active)
    if updated is None:
        return make_response(jsonify({"error": "user ID not found"}), 500)

    return make_response(jsonify(updated), 200)


# Delete
@app.route("/users/<userid>", methods=["DELETE"])
def del_user(userid):
    deleted = delete_user(userid)
    if deleted is None:
        return make_response(jsonify({"error": "user ID not found"}), 500)

    return make_response(jsonify(deleted), 200)


if __name__ == "__main__":
    print("Server running in port %s" % (USER_PORT))
    app.run(host=HOST, port=USER_PORT)
