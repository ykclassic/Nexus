import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from engine.runner import run_engine
from engine.elite_logger import log_event, log_error


def main():
    try:
        log_event("🚀 Nexus Engine Bootstrapped")
        results = run_engine()
        log_event(f"✅ Engine finished. Signals generated: {len(results)}")
    except Exception as e:
        log_error(f"❌ Engine crashed: {e}")
        raise e


if __name__ == "__main__":
    main()
