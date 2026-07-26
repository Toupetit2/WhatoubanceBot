import json
import os

def load_data():
    if not os.path.exists("data.json"):
        return {}

    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_data(data):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)