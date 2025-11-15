import json
import os
import requests
import grpc

# Assure-toi que ces deux modules sont accessibles depuis Booking :
# -> copie times_pb2.py et times_pb2_grpc.py générés depuis le .proto
import times_pb2
import times_pb2_grpc

script_dir = os.path.dirname(os.path.abspath(__file__))

# Cible du service Schedule gRPC (change en "schedule:3202" si tu es en docker-compose)
SCHEDULE_GRPC_TARGET = os.getenv("SCHEDULE_GRPC_TARGET", "localhost:3202")


def booking_by_user(_, info, userid):
    # TODO : Vérifier l'authentification
    with open(f'{script_dir}/data/bookings.json', "r") as file:
        bookings = json.load(file)
    for booking in bookings['bookings']:
        if booking['userid'] == userid:
            return booking
    return None


def add_booking(_, info, userid, dates):
    with open(f'{script_dir}/data/bookings.json', "r") as rfile:
        bookings = json.load(rfile)

    # Vérifier si l'utilisateur a déjà des réservations
    for booking in bookings['bookings']:
        if booking['userid'] == userid:
            # debug :
            print(f"User {userid} already has a booking.")
            return None  # L'utilisateur existe déjà

    # Valider que l'utilisateur existe via appel REST au service User
    try:
        resp = requests.get(f"http://localhost:3203/users/{userid}")
        if resp.status_code != 200:
            print(f"User {userid} not found in User service.")
            return None  # Utilisateur non trouvé
    except Exception as e:
        print(f"Error contacting User service: {e}")
        return None  # Service User indisponible

    # ------------------------------------------------------------------
    # Valider les dates et films via appel gRPC au service Schedule
    # pour chaque date dans dates:
    #   - vérifier si la date existe dans le planning
    #   - vérifier si chaque film est disponible à cette date
    # ------------------------------------------------------------------
    #
    # On suppose que "dates" ressemble à :
    # dates = [
    #   { "date": "2025-11-15", "movies": ["id1", "id2"] },
    #   ...
    # ]
    #
    # Si ce n'est pas exactement ça, adapte les clés (date/movies) en conséquence.

    try:
        with grpc.insecure_channel(SCHEDULE_GRPC_TARGET) as channel:
            stub = times_pb2_grpc.TimesStub(channel)

            for date_entry in dates:
                date_str = date_entry.get("date")
                movies_for_date = date_entry.get("movies", [])

                if not date_str:
                    print("Invalid date entry (missing 'date').")
                    return None

                # Appel gRPC : GetScheduleByDate(date)
                try:
                    schedule_reply = stub.GetScheduleByDate(
                        times_pb2.DateRequest(date=date_str)
                    )
                except grpc.RpcError as e:
                    # Si le service Schedule répond avec NOT_FOUND / UNAVAILABLE / etc.
                    print(f"Error from Schedule service for date {date_str}: {e.code()} {e.details()}")
                    return None

                # Si pas d'exception, la date existe et on a le planning de cette date
                scheduled_movies = set(schedule_reply.day.movies)

                # Vérifier que tous les films de la réservation pour cette date
                # sont bien dans le planning de cette date
                for movie_id in movies_for_date:
                    if movie_id not in scheduled_movies:
                        print(f"Movie {movie_id} is not available on date {date_str}.")
                        return None

    except Exception as e:
        print(f"Error while validating dates with Schedule service: {e}")
        return None

    # ----------------- Fin validation Schedule ------------------------

    # Créer nouvelle réservation
    new_booking = {
        "userid": userid,
        "dates": dates
    }

    bookings['bookings'].append(new_booking)

    with open(f'{script_dir}/data/bookings.json', "w") as wfile:
        json.dump(bookings, wfile, indent=2)

    return new_booking


def delete_booking(_, info, userid):
    # TODO : Vérifier l'authentification
    with open(f'{script_dir}/data/bookings.json', "r") as rfile:
        bookings = json.load(rfile)

    # Trouver et supprimer la réservation
    for booking in bookings['bookings']:
        if booking['userid'] == userid:
            bookings['bookings'].remove(booking)

            with open(f'{script_dir}/data/bookings.json', "w") as wfile:
                json.dump(bookings, wfile, indent=2)

            return booking

    return None  # Utilisateur non trouvé
