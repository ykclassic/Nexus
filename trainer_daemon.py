import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.runner import run_engine
import time

if __name__ == "__main__":
    # 🔴 Remove the while loop
    run_engine()
    print("✅ Engine completed successfully")
