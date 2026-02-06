import time
# REMOVED: from Nexus.engine.elite_logger import log_error
# FIXED: Use the engine package path recognized by trainer_daemon.py
from engine.elite_logger import log_error

def safe_call(func, retries=3, delay=2):
    for i in range(retries):
        try:
            return func()
        except Exception as e:
            log_error("Exchange call failed", {"attempt": i+1, "error": str(e)})
            time.sleep(delay)
    return None
