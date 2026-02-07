from engine.runner import run_engine
from engine.db import init_db

def main():
    print("🚀 Starting Nexus Engine...")
    init_db()
    run_engine()

if __name__ == "__main__":
    main()
