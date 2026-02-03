import os
import requests
import time
from engine.elite_logger import log_event, log_error

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")


def send_discord_alert(signal: dict, retries=3):
    if not DISCORD_WEBHOOK:
        log_error("Discord webhook not set")
        return

    msg = (
        f"🚨 **NEXUS SIGNAL**\n"
        f"Symbol: {signal['symbol']}\n"
        f"Direction: {signal['direction']}\n"
        f"Entry: {signal['entry']}\n"
        f"SL: {signal['sl']}\n"
        f"TP: {signal['tp']}\n"
        f"Confidence: {signal['confidence']}%"
    )

    payload = {"content": msg}

    for attempt in range(retries):
        try:
            r = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
            if r.status_code == 204:
                log_event("Discord alert sent successfully")
                return
            else:
                log_error(f"Discord error: {r.text}")
        except Exception as e:
            log_error(f"Discord exception: {str(e)}")

        time.sleep(2)

    log_error("Discord alert failed after retries")
