# Nexus/engine/exchange_retry.py

import time
from Nexus.engine.elite_logger import log_error


def safe_call(func, retries=3, delay=2):
    for i in range(retries):
        try:
            return func()
        except Exception as e:
            log_error(f"Exchange call failed (attempt {i+1}) → {e}")
            time.sleep(delay)
    return None
