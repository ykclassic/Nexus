def validate_trade(entry, sl, tp) -> bool:
    risk = abs(entry - sl)
    reward = abs(tp - entry)

    # Risk/Reward rule
    if reward / risk < 2:
        return False

    return True
