# engine/signal_engine.py

from engine.exchange import fetch_price
from engine.intelligence.signal_scoring import score

def generate_signal(symbol: str):
    price = fetch_price(symbol)

    # New institutional logic: volatility breakout + momentum bias
    momentum = (price % 10) / 10  # placeholder logic (replace with real indicators later)
    volatility = (price % 100) / 100

    if momentum > 0.6 and volatility > 0.4:
        direction = "LONG"
        base_conf = 0.78
        strategy = "volatility_momentum"
    elif momentum < 0.3 and volatility > 0.4:
        direction = "SHORT"
        base_conf = 0.76
        strategy = "volatility_momentum"
    else:
        return None

    final_conf = score(base_conf, strategy)

    return {
        "symbol": symbol,
        "timeframe": "1h",
        "direction": direction,
        "strategy": strategy,
        "price": price,
        "confidence": final_conf
    }
