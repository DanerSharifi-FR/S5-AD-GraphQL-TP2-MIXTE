import os
import json
from concurrent import futures

import grpc
import requests

import times_pb2
import times_pb2_grpc

# Config
PORT = 3202
MOVIE_GRAPHQL_URL = os.getenv("MOVIE_GRAPHQL_URL", "http://127.0.0.1:3001/graphql")

# Chargement de la "DB" times.json
script_dir = os.path.dirname(os.path.abspath(__file__))
times_path = os.path.join(script_dir, "data", "times.json")

with open(times_path, "r") as jsf:
    schedule = json.load(jsf)["schedule"]


def write(schedule_data):
    with open(times_path, "w") as f:
        json.dump({"schedule": schedule_data}, f)


class TimesService(times_pb2_grpc.TimesServicer):
    # GET /schedule/<date> -> GetScheduleByDate
    def GetScheduleByDate(self, request, context):
        for day in schedule:
            if str(day["date"]) == str(request.date):
                day_msg = times_pb2.ScheduleDay(
                    date=day["date"],
                    movies=day["movies"]
                )
                return times_pb2.TimesReply(
                    message="OK",
                    day=day_msg
                )

        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("Date not found")
        return times_pb2.TimesReply(error="Date not found")

    # POST /schedule -> AddSchedule
    def AddSchedule(self, request, context):
        # request: ScheduleDay (date + movies)
        for day in schedule:
            if str(day["date"]) == str(request.date):
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
                    json={'query': query},
                    timeout=3
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

        # Si tout est OK, on ajoute le jour
        new_day = {
            "date": request.date,
            "movies": list(request.movies)
        }
        schedule.append(new_day)
        write(schedule)

        return times_pb2.TimesReply(message="Date added")

    # DELETE /schedule/<date> -> DeleteSchedule
    def DeleteSchedule(self, request, context):
        for day in list(schedule):
            if str(day["date"]) == str(request.date):
                schedule.remove(day)
                write(schedule)

                day_msg = times_pb2.ScheduleDay(
                    date=day["date"],
                    movies=day["movies"]
                )
                return times_pb2.TimesReply(
                    message="Date deleted",
                    day=day_msg
                )

        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("Date not found")
        return times_pb2.TimesReply(error="Date not found")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    times_pb2_grpc.add_TimesServicer_to_server(TimesService(), server)
    server.add_insecure_port(f"[::]:{PORT}")
    server.start()
    print(f"gRPC Times server (schedule.py) running on port {PORT}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
