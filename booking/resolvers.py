import json
import os
import requests

script_dir = os.path.dirname(os.path.abspath(__file__))

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
    '''try:
        resp = requests.get(f"http://localhost:3203/users/{userid}")
        if resp.status_code != 200:
            # debug :
            print(f"User service returned status code {resp.status_code} for user {userid}.")
            # print (resp.json()) for debug
            print(resp.text)
            return None  # Utilisateur invalide
    except Exception as e:
        print(f"Error contacting User service: {e}")
        return None  # Service User indisponible'''

    # todo: valider les dates et films via appel gRPC au service Schedule
    # pour chaque date dans dates:
    #   - vérifier si la date existe dans le planning
    #   - vérifier si chaque film est disponible à cette date

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