import logging
import json
import traceback
from datetime import datetime
import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
        }

        if hasattr(record, "extra_data"):
            log_record.update(record.extra_data)

        if record.exc_info:
            log_record["traceback"] = traceback.format_exc()

        return json.dumps(log_record)


def get_logger(name="NEXUS_ENGINE"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger  # prevent duplicate handlers

    formatter = JsonFormatter()

    # Console handler (GitHub Actions friendly)
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)

    # File handler
    fh = logging.FileHandler(f"{LOG_DIR}/nexus.log")
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger


LOGGER = get_logger()


def log_event(event, **kwargs):
    LOGGER.info(event, extra={"extra_data": {"event": event, **kwargs}})


def log_error(event, error: Exception, **kwargs):
    LOGGER.error(
        event,
        extra={"extra_data": {"event": event, "error": str(error), **kwargs}},
        exc_info=True,
    )
