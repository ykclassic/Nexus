from .notifier import send
from .logger import log_error
from .exchange import safe_fetch
from .config import TIMEFRAME

def update_trades(exchange, conn):
    c = conn.cursor()

    c.execute("""
        SELECT id, symbol, signal_type, entry, tp, sl
        FROM signals WHERE status='OPEN'
    """)

    for sid, symbol, side, entry, tp, sl in c.fetchall():
        try:
            ohlcv = safe_fetch(exchange, symbol, TIMEFRAME, limit=1)
            if not ohlcv:
                continue

            price = ohlcv[-1][4]
            status = None

            if side == "LONG":
                if price <= sl: status = "SL"
                elif price >= tp: status = "TP"
            else:
                if price >= sl: status = "SL"
                elif price <= tp: status = "TP"

            if status:
                pnl = ((price - entry) / entry) * 100
                if side == "SHORT":
                    pnl = -pnl

                c.execute("""
                    UPDATE signals
                    SET status=?, exit_price=?, exit_time=datetime('now'),
                        result=?, updated_at=datetime('now')
                    WHERE id=?
                """, (status, price, pnl, sid))

                conn.commit()
                send(f"📊 {symbol} {side} closed: {status} | PnL {pnl:.2f}%")

        except Exception as e:
            log_error(symbol, e)
