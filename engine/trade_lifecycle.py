from elite_logger import log_event
from discord_alert import send_discord_alert

class TradeLifecycle:
    def __init__(self):
        self.trades = {}

    def open_trade(self, trade_id, symbol, entry, sl, tp, confidence):
        trade = {
            "status": "OPEN",
            "symbol": symbol,
            "entry": entry,
            "sl": sl,
            "tp": tp,
            "confidence": confidence,
        }

        self.trades[trade_id] = trade

        log_event("TRADE_OPENED", trade_id=trade_id, **trade)

        send_discord_alert(
            "🚀 NEW ELITE SIGNAL",
            f"{symbol} trade opened",
            trade,
        )

    def close_trade(self, trade_id, result, price):
        if trade_id not in self.trades:
            return

        trade = self.trades[trade_id]
        trade["status"] = "CLOSED"
        trade["result"] = result
        trade["close_price"] = price

        log_event("TRADE_CLOSED", trade_id=trade_id, **trade)

        send_discord_alert(
            "✅ TRADE CLOSED",
            f"{trade['symbol']} hit {result}",
            trade,
        )
