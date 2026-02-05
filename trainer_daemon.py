# trainer_daemon.py

import sys
import os

# Add project root to Python path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

from engine.runner import run_engine


if __name__ == "__main__":
    run_engine()
