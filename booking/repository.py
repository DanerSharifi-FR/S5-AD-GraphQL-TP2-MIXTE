# booking/repository.py
import os
import json

from pymongo import MongoClient

from config import USE_MONGO, MONGO_URI, MONGO_DB_NAME

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

BOOKINGS_JSON_PATH = os.path.join(SCRIPT_DIR, "databases", "bookings.json")

_client = None
_db = None
_bookings_col = None

if USE_MONGO:
    print(f"[booking/repository] USE_MONGO=1, connexion à {MONGO_URI}, base={MONGO_DB_NAME}")
    _client = MongoClient(MONGO_URI)
    _db = _client[MONGO_DB_NAME]
    _bookings_col = _db["bookings"]
else:
    print("[booking/repository] USE_MONGO=0, utilisation des fichiers JSON locaux")


def _load_json_bookings():
    if not os.path.exists(BOOKINGS_JSON_PATH):
        return []

    with open(BOOKINGS_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        return data.get("bookings", [])
    return data


def _write_json_bookings(bookings_list):
    os.makedirs(os.path.dirname(BOOKINGS_JSON_PATH), exist_ok=True)
    with open(BOOKINGS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump({"bookings": bookings_list}, f, ensure_ascii=False, indent=2)


def get_all_bookings():
    if USE_MONGO:
        return list(_bookings_col.find({}, {"_id": 0}))
    return _load_json_bookings()


def get_booking_by_userid(userid: str):
    if USE_MONGO:
        return _bookings_col.find_one({"userid": str(userid)}, {"_id": 0})

    for booking in _load_json_bookings():
        if str(booking.get("userid")) == str(userid):
            return booking
    return None


def add_booking(booking: dict):
    """
    booking = {
      "userid": "...",
      "dates": [
        { "date": "...", "movies": ["id1", "id2"] },
        ...
      ]
    }
    """
    userid = booking.get("userid")
    if not userid:
        return None

    userid_str = str(userid)
    booking["userid"] = userid_str

    if USE_MONGO:
        if _bookings_col.find_one({"userid": userid_str}):
            return None
        _bookings_col.insert_one(booking)
        return _bookings_col.find_one({"userid": userid_str}, {"_id": 0})

    bookings_list = _load_json_bookings()
    for b in bookings_list:
        if str(b.get("userid")) == userid_str:
            return None

    bookings_list.append(booking)
    _write_json_bookings(bookings_list)
    return booking


def delete_booking_by_userid(userid: str):
    userid_str = str(userid)

    if USE_MONGO:
        deleted = _bookings_col.find_one({"userid": userid_str}, {"_id": 0})
        if not deleted:
            return None
        _bookings_col.delete_one({"userid": userid_str})
        return deleted

    bookings_list = _load_json_bookings()
    deleted_booking = None
    remaining = []

    for b in bookings_list:
        if deleted_booking is None and str(b.get("userid")) == userid_str:
            deleted_booking = b
        else:
            remaining.append(b)

    if deleted_booking is not None:
        _write_json_bookings(remaining)

    return deleted_booking
