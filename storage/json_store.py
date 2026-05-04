import json
import os

SAVE_FILE = "rooms.json"


def load_previous():
    if not os.path.exists(SAVE_FILE):
        return []

    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_current(data):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def diff_rooms(old, new):
    old_ids = set(r["id"] for r in old)
    return [r for r in new if r["id"] not in old_ids]