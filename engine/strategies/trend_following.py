def trend_following_signal(features):
    if features["trend_strength"] > 0.6 and features["momentum"] > 0.4:
        return True
    return False
