import logging
import os
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "nexus.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("Nexus")


def log_event(message: str):
    logger.info(message)


def log_error(message: str):
    logger.error(message)


def log_signal(signal: dict):
    logger.info(f"SIGNAL | {signal}")
