import json
import os

WHITELIST_FILE = "whitelist.json"


def _load_whitelist() -> dict:
    if not os.path.exists(WHITELIST_FILE):
        return {}
    try:
        with open(WHITELIST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def _save_whitelist(data: dict):
    with open(WHITELIST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def is_in_whitelist(owner_id: int, member_id: int) -> bool:
    data = _load_whitelist()
    return member_id in data.get(str(owner_id), [])


def add_to_whitelist(owner_id: int, member_id: int):
    data = _load_whitelist()
    key = str(owner_id)
    if key not in data:
        data[key] = []
    if member_id not in data[key]:
        data[key].append(member_id)
    _save_whitelist(data)


def remove_from_whitelist(owner_id: int, member_id: int):
    data = _load_whitelist()
    key = str(owner_id)
    if key in data and member_id in data[key]:
        data[key].remove(member_id)
        _save_whitelist(data)


def get_whitelist(owner_id: int) -> list[int]:
    data = _load_whitelist()
    return data.get(str(owner_id), [])


def clear_whitelist(owner_id: int):
    data = _load_whitelist()
    key = str(owner_id)
    if key in data:
        del data[key]
        _save_whitelist(data)