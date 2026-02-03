import requests
import time
from elite_logger import log_event, log_error

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")  # store in GitHub Secrets

MAX_RETRIES = 5
RETRY_DELAY = 2  # seconds


def send_discord_alert(title, message, data=None):
    if not DISCORD_WEBHOOK:
        log_error("DISCORD_WEBHOOK_MISSING", Exception("Webhook not set"))
        return

    payload = {
        "embeds": [
            {
                "title": title,
                "description": message,
                "color": 65280,
                "fields": [
                    {"name": k, "value": str(v), "inline": True}
                    for k, v in (data or {}).items()
                ],
            }
        ]
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            res = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)

            if res.status_code in [200, 204]:
                log_event("DISCORD_ALERT_SENT", attempt=attempt)
                return True
            else:
                raise Exception(f"HTTP {res.status_code}")

        except Exception as e:
            log_error("DISCORD_ALERT_FAILED", e, attempt=attempt)
            time.sleep(RETRY_DELAY * attempt)

    return False
