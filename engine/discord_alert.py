import requests
import os
from engine.elite_logger import log_error, log_event

def send_discord_alert(signal):
    # Fetch directly from OS environment to ensure GitHub Secrets are captured
    webhook_url = os.getenv("DISCORD_WEBHOOK")

    if not webhook_url:
        log_error("📡 Discord Webhook URL not found in Environment (check GitHub Secrets).")
        return

    # Vibrant colors for clear visual distinction
    # 3066993 = Green, 15158332 = Red
    color = 3066993 if signal['side'] == 'LONG' else 15158332 
    
    payload = {
        "username": "Nexus Command Centre",
        "embeds": [{
            "title": f"🚀 NEXUS SIGNAL: {signal['symbol']}",
            "color": color,
            "fields": [
                {"name": "Action", "value": f"**{signal['side']}**", "inline": True},
                {"name": "Accuracy", "value": f"**{signal['confidence']}%**", "inline": True},
                {"name": "Entry Price", "value": f"${signal['entry']:,.4f}", "inline": False},
                {"name": "Take Profit", "value": f"**${signal['tp']:,.4f}**", "inline": True},
                {"name": "Stop Loss", "value": f"${signal['sl']:,.4f}", "inline": True}
            ],
            "footer": {"text": "Nexus Intelligence Engine v2.0"},
        }]
    }

    try:
        # Increased timeout to 15s for GitHub runner latency
        response = requests.post(webhook_url, json=payload, timeout=15)
        if response.status_code in [200, 204]:
            log_event(f"✅ Discord alert dispatched: {signal['symbol']}")
        else:
            log_error(f"❌ Discord API Error: {response.status_code} - {response.text}")
    except Exception as e:
        log_error(f"❌ Discord Webhook Exception: {e}")
