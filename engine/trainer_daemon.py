from engine.db import init_db
from engine.runner import run_engine

if __name__ == "__main__":
    init_db()
    run_engine()
