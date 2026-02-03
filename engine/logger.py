import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def log_error(ctx, e):
    logging.error(f"[{ctx}] {type(e).__name__}: {e}")
