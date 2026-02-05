# trainer_daemon.py

import sys, os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)

from Nexus.engine.runner import run_engine


if __name__ == "__main__":
    print("🚀 Nexus Engine Booting...")
    run_engine()
    print("✅ Nexus Engine Finished")
