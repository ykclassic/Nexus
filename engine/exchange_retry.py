import time
from elite_logger import log_error, log_event

def safe_exchange_call(func, *args, retries=5, delay=2, **kwargs):
    for attempt in range(1, retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log_error("EXCHANGE_CALL_FAILED", e, attempt=attempt)
            time.sleep(delay * attempt)

    log_event("EXCHANGE_CALL_ABORTED")
    return None
