import requests
import os
from engine.config import DISCORD_WEBHOOK
from engine.elite_logger import log_error, log_event

def send_discord_alert(signal):
    if not DISCORD_WEBHOOK:
        log_error("Discord Webhook URL not found in environment.")
        return

    # Color coding: Green for LONG, Red for SHORT
    color = 5763719 if signal['side'] == 'LONG' else 15548997
    
    payload = {
        "username": "Nexus Elite",
        "avatar_url": "https://i.imgur.com/4SshYFk.png",
        "embeds": [{
            "title": f"🚀 NEW SIGNAL: {signal['symbol']}",
            "color": color,
            "fields": [
                {"name": "Direction", "value": f"**{signal['side']}**", "inline": True},
                {"name": "Confidence", "value": f"**{signal['confidence']}%**", "inline": True},
                {"name": "Entry Price", "value": f"${signal['entry']:,.4f}", "inline": False},
                {"name": "Target (TP)", "value": f"**${signal['tp']:,.4f}**", "inline": True},
                {"name": "Stop Loss (SL)", "value": f"${signal['sl']:,.4f}", "inline": True}
            ],
            "footer": {"text": "Nexus Intelligence Layer • Quality over Quantity"},
            "timestamp": None # Discord auto-stamps if omitted
        }]
    }

    try:
        response = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
        if response.status_code in [200, 204]:
            log_event(f"📡 Discord alert sent for {signal['symbol']}")
        else:
            log_error(f"Failed to send Discord alert: {response.status_code} - {response.text}")
    except Exception as e:
        log_error(f"Webhook Exception: {e}")
