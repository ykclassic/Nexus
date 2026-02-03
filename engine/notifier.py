import os, requests, time
from .logger import log_error

WEBHOOK = os.getenv("DISCORD_WEBHOOK")

def send(msg):
    if not WEBHOOK:
        return
    
    for i in range(3):
        try:
            r = requests.post(WEBHOOK, json={"content": msg}, timeout=10)
            if r.status_code in [200, 204]:
                return
        except Exception as e:
            log_error("DISCORD", e)
        time.sleep(2)
