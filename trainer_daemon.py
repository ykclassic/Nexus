# trainer_daemon.py

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.runner import run_engine

if __name__ == "__main__":
    run_engine()
