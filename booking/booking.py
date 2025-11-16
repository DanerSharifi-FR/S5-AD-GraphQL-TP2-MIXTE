from ariadne import (
    graphql_sync,
    make_executable_schema,
    load_schema_from_path,
    ObjectType,
    QueryType,
    MutationType,
)
from flask import Flask, request, jsonify, make_response
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

import resolvers as r
from config import HOST, BOOKING_PORT

app = Flask(__name__)
PORT = int(BOOKING_PORT)

SCHEMA_PATH = os.path.join(CURRENT_DIR, "booking.graphql")
type_defs = load_schema_from_path(SCHEMA_PATH)

query = QueryType()
mutation = MutationType()
booking = ObjectType("Booking")
date_booking = ObjectType("DateBooking")

query.set_field("booking_by_user", r.booking_by_user)
mutation.set_field("add_booking", r.add_booking)
mutation.set_field("delete_booking", r.delete_booking)

schema = make_executable_schema(type_defs, booking, query, mutation, date_booking)


@app.route("/", methods=["GET"])
def home():
    return make_response("<h1 style='color:blue'>Welcome to the Booking service!</h1>", 200)


@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value=data,
        debug=app.debug,
    )
    status_code = 200 if success else 400
    return jsonify(result), status_code


if __name__ == "__main__":
    print(f"Server running in port {PORT}")
    app.run(host=HOST, port=PORT)
