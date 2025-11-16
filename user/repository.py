# user/repository.py
import os
import json

from pymongo import MongoClient

from config import USE_MONGO, MONGO_URI, MONGO_DB_NAME

script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, "databases", "users.json")

_client = None
_db = None
_users_col = None

if USE_MONGO:
    _client = MongoClient(MONGO_URI)
    _db = _client[MONGO_DB_NAME]
    _users_col = _db["users"]


def _load_json_users():
    if not os.path.exists(json_path):
        return []

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        return data.get("users", [])
    return data


def _write_json_users(users):
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"users": users}, f, ensure_ascii=False, indent=2)


def get_all_users():
    if USE_MONGO:
        return list(_users_col.find({}, {"_id": 0}))
    return _load_json_users()


def get_user_by_id(user_id: str):
    if USE_MONGO:
        return _users_col.find_one({"id": str(user_id)}, {"_id": 0})

    for user in _load_json_users():
        if str(user.get("id")) == str(user_id):
            return user
    return None


def get_user_by_name(name: str):
    if USE_MONGO:
        return _users_col.find_one({"name": name}, {"_id": 0})

    for user in _load_json_users():
        if str(user.get("name")) == str(name):
            return user
    return None


def add_user(user: dict):
    # harmoniser l'id en string comme ton code actuel
    if "id" in user:
        user["id"] = str(user["id"])

    user_id = user.get("id")
    if not user_id:
        # on laisse la route gérer l'erreur si besoin
        return None

    if USE_MONGO:
        if _users_col.find_one({"id": user_id}):
            return None
        _users_col.insert_one(user)
        return _users_col.find_one({"id": user_id}, {"_id": 0})

    users = _load_json_users()
    for u in users:
        if str(u.get("id")) == str(user_id):
            return None

    users.append(user)
    _write_json_users(users)
    return user


def update_user_last_active(user_id: str, last_active: str):
    if USE_MONGO:
        res = _users_col.update_one(
            {"id": str(user_id)},
            {"$set": {"last_active": last_active}},
        )
        if res.matched_count == 0:
            return None
        return _users_col.find_one({"id": str(user_id)}, {"_id": 0})

    users = _load_json_users()
    updated_user = None

    for u in users:
        if str(u.get("id")) == str(user_id):
            u["last_active"] = last_active
            updated_user = u
            break

    if updated_user is not None:
        _write_json_users(users)

    return updated_user


def delete_user(user_id: str):
    if USE_MONGO:
        deleted = _users_col.find_one({"id": str(user_id)}, {"_id": 0})
        if not deleted:
            return None
        _users_col.delete_one({"id": str(user_id)})
        return deleted

    users = _load_json_users()
    deleted_user = None
    remaining = []

    for u in users:
        if deleted_user is None and str(u.get("id")) == str(user_id):
            deleted_user = u
        else:
            remaining.append(u)

    if deleted_user is not None:
        _write_json_users(remaining)

    return deleted_user
