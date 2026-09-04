import json
import os
from datetime import date

USAGE_FILE = "usage_tracker.json"
DAILY_LIMIT = 20  # Free tier limit — paid tier lene par isko badha dena

def _load_usage():
    if not os.path.exists(USAGE_FILE):
        return {"date": str(date.today()), "count": 0}
    with open(USAGE_FILE, "r") as f:
        data = json.load(f)
    # Agar naya din hai to counter reset karo
    if data.get("date") != str(date.today()):
        data = {"date": str(date.today()), "count": 0}
    return data

def _save_usage(data):
    with open(USAGE_FILE, "w") as f:
        json.dump(data, f)

def get_remaining_quota():
    data = _load_usage()
    return max(0, DAILY_LIMIT - data["count"])

def increment_usage(n=1):
    data = _load_usage()
    data["count"] += n
    _save_usage(data)

def get_today_usage():
    data = _load_usage()
    return data["count"], DAILY_LIMIT