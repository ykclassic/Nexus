import requests
from engine.elite_logger import log_event, log_error

DISCORD_WEBHOOK = "YOUR_DISCORD_WEBHOOK"

def send_discord_alert(signal):
    try:
        msg = f"""
🚨 **NEXUS SIGNAL**

Pair: {signal['pair']}
Direction: {signal['direction']}
Entry: {signal['entry']}
Stop Loss: {signal['sl']}
Take Profit: {signal['tp']}
Confidence: {signal['confidence']}%
        """

        payload = {"content": msg}
        r = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)

        if r.status_code == 204:
            log_event("Discord alert sent", signal)
        else:
            log_error("Discord webhook failed", {"status": r.status_code})

    except Exception as e:
        log_error("Discord alert exception", {"error": str(e)})
