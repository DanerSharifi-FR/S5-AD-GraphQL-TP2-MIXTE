# booking/resolvers.py
import os
import sys
import requests
import grpc

# Générés à partir du .proto, copiés dans booking/
import times_pb2
import times_pb2_grpc

# chemins pour importer config + repository
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

import repository as repo
from config import USER_SERVICE_URL, SCHEDULE_PORT, USER_PORT, SCHEDULE_SERVICE_URL

# Cible du service Schedule gRPC
# - hors Docker : localhost:<SCHEDULE_PORT>
# - en Docker   : override via SCHEDULE_GRPC_TARGET
SCHEDULE_GRPC_TARGET = f"{SCHEDULE_SERVICE_URL}:{SCHEDULE_PORT}"


def booking_by_user(_, info, userid):
    # TODO : Auth si besoin
    booking = repo.get_booking_by_userid(userid)
    return booking


def add_booking(_, info, userid, dates):
    # 1. Vérifier si l'utilisateur a déjà des réservations
    existing = repo.get_booking_by_userid(userid)
    if existing is not None:
        print(f"User {userid} already has a booking.")
        return None

    # 2. Valider que l'utilisateur existe via service User (REST)
    try:
        resp = requests.get(f"{USER_SERVICE_URL}:{USER_PORT}/users/{userid}", timeout=3)
        if resp.status_code != 200:
            print(f"User {userid} not found in User service. status={resp.status_code}")
            return None
    except Exception as e:
        print(f"Error contacting User service: {e}")
        return None

    # 3. Valider dates & films via gRPC Schedule (Times)
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
                    print(f"Error from Schedule service for date {date_str}: {e.code()} {e.details()}")
                    return None

                scheduled_movies = set(schedule_reply.day.movies)

                for movie_id in movies_for_date:
                    if movie_id not in scheduled_movies:
                        print(f"Movie {movie_id} is not available on date {date_str}.")
                        return None

    except Exception as e:
        print(f"Error while validating dates with Schedule service: {e}")
        return None

    # 4. Créer nouvelle réservation
    booking_doc = {
        "userid": str(userid),
        "dates": dates,
    }

    created = repo.add_booking(booking_doc)
    if created is None:
        print(f"User {userid} already has a booking (repo refused).")
        return None

    return created


def delete_booking(_, info, userid):
    # TODO : Auth si besoin
    deleted = repo.delete_booking_by_userid(userid)
    if deleted is None:
        print(f"Booking for user {userid} not found.")
        return None
    return deleted
