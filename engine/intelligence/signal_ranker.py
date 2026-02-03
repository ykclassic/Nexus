def select_elite_signals(signals, limit=2):
    signals = sorted(signals, key=lambda s: s["confidence"], reverse=True)
    return signals[:limit]
