import datetime
import json
import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def _write_log(level, message, data=None):
    timestamp = datetime.datetime.utcnow().isoformat()
    log_entry = {
        "time": timestamp,
        "level": level,
        "message": message,
        "data": data or {}
    }

    log_file = os.path.join(LOG_DIR, "nexus.log")
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

def log_event(message, data=None):
    _write_log("EVENT", message, data)

def log_error(message, data=None):
    _write_log("ERROR", message, data)
