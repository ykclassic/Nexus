import requests
import os
from engine.config import DISCORD_WEBHOOK
from engine.elite_logger import log_error, log_event

def send_discord_alert(signal):
    if not DISCORD_WEBHOOK:
        log_error("📡 Discord Webhook URL not configured in Environment/Secrets.")
        return

    # Vibrant colors for clear visual distinction
    color = 3066993 if signal['side'] == 'LONG' else 15158332 # Green or Red
    
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
            "timestamp": None
        }]
    }

    try:
        response = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
        if response.status_code in [200, 204]:
            log_event(f"✅ Discord alert dispatched: {signal['symbol']}")
        else:
            log_error(f"❌ Discord API Error: {response.status_code}")
    except Exception as e:
        log_error(f"❌ Discord Webhook Exception: {e}")
