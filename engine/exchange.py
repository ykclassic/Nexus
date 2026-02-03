import ccxt, time
from .logger import log_error

def create_exchange():
    return ccxt.gateio({
        "enableRateLimit": True,
        "timeout": 10000,
    })

def safe_fetch(exchange, symbol, timeframe, limit=50, retries=3):
    for i in range(retries):
        try:
            data = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            if data and len(data) > 0:
                return data
        except Exception as e:
            log_error(symbol, e)
            time.sleep(2)
    return None
