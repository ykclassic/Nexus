from engine.exchange import fetch_price
from engine.strategies.liquidity_sweep import detect as liquidity_sweep
from engine.intelligence.signal_scoring import score

def generate_signal(symbol: str):
    price = fetch_price(symbol)

    # Example elite logic (can be replaced with AI later)
    if liquidity_sweep(price):
        direction = "LONG"
        base_conf = 0.82
        strategy = "liquidity_sweep"
    else:
        return None

    final_conf = score(base_conf, strategy)

    return {
        "asset": symbol,
        "direction": direction,
        "confidence": final_conf,
        "price": price,
        "strategy": strategy
    }
