# engine/exchange_retry.py

import time
from engine.elite_logger import log_error


def safe_call(func, *args, retries=3, delay=2, **kwargs):
    for i in range(retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log_error("Exchange call failed", {"attempt": i + 1, "error": str(e)})
            time.sleep(delay)
    return None
