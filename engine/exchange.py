import random

def fetch_price(symbol: str) -> float:
    return round(random.uniform(20000, 60000), 2)
