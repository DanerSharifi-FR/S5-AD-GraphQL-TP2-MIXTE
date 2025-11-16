# schedule/repository.py
import os
import json

from pymongo import MongoClient

from config import USE_MONGO, MONGO_URI, MONGO_DB_NAME

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TIMES_JSON_PATH = os.path.join(SCRIPT_DIR, "databases", "times.json")

_client = None
_db = None
_schedule_col = None

if USE_MONGO:
    print(f"[schedule/repository] USE_MONGO=1, connexion à {MONGO_URI}, base={MONGO_DB_NAME}")
    _client = MongoClient(MONGO_URI)
    _db = _client[MONGO_DB_NAME]
    _schedule_col = _db["times"]
else:
    print("[schedule/repository] USE_MONGO=0, utilisation des fichiers JSON locaux")


def _load_json_schedule():
    if not os.path.exists(TIMES_JSON_PATH):
        return []

    with open(TIMES_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        return data.get("schedule", [])
    return data


def _write_json_schedule(schedule_list):
    os.makedirs(os.path.dirname(TIMES_JSON_PATH), exist_ok=True)
    with open(TIMES_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump({"schedule": schedule_list}, f, ensure_ascii=False, indent=2)


def get_all_schedule():
    if USE_MONGO:
        return list(_schedule_col.find({}, {"_id": 0}))
    return _load_json_schedule()


def get_schedule_by_date(date_str: str):
    if USE_MONGO:
        return _schedule_col.find_one({"date": str(date_str)}, {"_id": 0})

    for day in _load_json_schedule():
        if str(day.get("date")) == str(date_str):
            return day
    return None


def add_schedule_entry(day: dict):
    """
    day = {"date": "...", "movies": ["id1", "id2", ...]}
    Retourne le jour créé, ou None si la date existe déjà.
    """
    date_value = day.get("date")
    if not date_value:
        return None

    if USE_MONGO:
        if _schedule_col.find_one({"date": str(date_value)}):
            return None
        _schedule_col.insert_one(day)
        return _schedule_col.find_one({"date": str(date_value)}, {"_id": 0})

    schedule_list = _load_json_schedule()
    for d in schedule_list:
        if str(d.get("date")) == str(date_value):
            return None

    schedule_list.append(day)
    _write_json_schedule(schedule_list)
    return day


def delete_schedule_by_date(date_str: str):
    """
    Supprime le jour pour cette date.
    Retourne le jour supprimé ou None.
    """
    if USE_MONGO:
        deleted = _schedule_col.find_one({"date": str(date_str)}, {"_id": 0})
        if not deleted:
            return None
        _schedule_col.delete_one({"date": str(date_str)})
        return deleted

    schedule_list = _load_json_schedule()
    deleted_day = None
    remaining = []

    for d in schedule_list:
        if deleted_day is None and str(d.get("date")) == str(date_str):
            deleted_day = d
        else:
            remaining.append(d)

    if deleted_day is not None:
        _write_json_schedule(remaining)

    return deleted_day
