# trainer_daemon.py

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from engine.runner import run_engine


if __name__ == "__main__":
    run_engine()
