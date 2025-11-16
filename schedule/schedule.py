import os
import sys
from concurrent import futures

import grpc
import requests

import times_pb2
import times_pb2_grpc

# imports config + repository
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

import repository as repo
from config import SCHEDULE_PORT, MOVIE_SERVICE_URL, MOVIE_PORT

# Config
PORT = int(SCHEDULE_PORT)

# URL du service Movie en GraphQL
# - hors Docker : MOVIE_SERVICE_URL = http://localhost:3200 -> on ajoute /graphql
# - en Docker   : MOVIE_SERVICE_URL_DOCKER = http://movie-mixte:3200 -> idem
MOVIE_GRAPHQL_URL = os.getenv("MOVIE_GRAPHQL_URL", f"{MOVIE_SERVICE_URL}:{MOVIE_PORT}/graphql")


class TimesService(times_pb2_grpc.TimesServicer):
    # GET /schedule/<date> -> GetScheduleByDate
    def GetScheduleByDate(self, request, context):
        day = repo.get_schedule_by_date(request.date)
        if day is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Date not found")
            return times_pb2.TimesReply(error="Date not found")

        day_msg = times_pb2.ScheduleDay(
            date=day["date"],
            movies=day["movies"],
        )
        return times_pb2.TimesReply(message="OK", day=day_msg)

    # POST /schedule -> AddSchedule
    def AddSchedule(self, request, context):
        # Vérifier si la date existe déjà
        existing = repo.get_schedule_by_date(request.date)
        if existing is not None:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details("Date already exists")
            return times_pb2.TimesReply(error="Date already exists")

        # Vérif des movies via le service Movie en GraphQL
        try:
            for movie_id in request.movies:
                query = f'''
                {{
                  movie_with_id(_id: "{movie_id}") {{
                    id
                  }}
                }}
                '''

                resp = requests.post(
                    MOVIE_GRAPHQL_URL,
                    json={"query": query},
                    timeout=3,
                )

                if resp.status_code != 200:
                    context.set_code(grpc.StatusCode.UNAVAILABLE)
                    context.set_details("Movies service unavailable")
                    return times_pb2.TimesReply(error="Movies service unavailable")

                body = resp.json()

                # Erreur GraphQL ou film non trouvé
                if body.get("errors") or body.get("data", {}).get("movie_with_id") is None:
                    msg = f"Invalid movie ID: {movie_id}"
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details(msg)
                    return times_pb2.TimesReply(error=msg)

        except Exception as e:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details(f"Movies service unavailable: {e}")
            return times_pb2.TimesReply(error="Movies service unavailable")

        # Si tout est OK, on ajoute le jour via le repository
        new_day_dict = {
            "date": request.date,
            "movies": list(request.movies),
        }

        created = repo.add_schedule_entry(new_day_dict)
        if created is None:
            # sécurité au cas où
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details("Date already exists")
            return times_pb2.TimesReply(error="Date already exists")

        return times_pb2.TimesReply(message="Date added")

    # DELETE /schedule/<date> -> DeleteSchedule
    def DeleteSchedule(self, request, context):
        deleted = repo.delete_schedule_by_date(request.date)
        if deleted is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Date not found")
            return times_pb2.TimesReply(error="Date not found")

        day_msg = times_pb2.ScheduleDay(
            date=deleted["date"],
            movies=deleted["movies"],
        )
        return times_pb2.TimesReply(message="Date deleted", day=day_msg)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    times_pb2_grpc.add_TimesServicer_to_server(TimesService(), server)
    server.add_insecure_port(f"[::]:{PORT}")
    server.start()
    print(f"gRPC Times server (schedule.py) running on port {PORT}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
