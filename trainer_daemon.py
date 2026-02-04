import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.runner import run_engine
import time

if __name__ == "__main__":
    while True:
        run_engine()
        time.sleep(60)  # run every minute (you can change)
