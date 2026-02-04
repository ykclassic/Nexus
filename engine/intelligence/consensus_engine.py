from engine.strategies.trend_following import trend_following_signal
from engine.strategies.breakout import breakout_signal
from engine.strategies.mean_reversion import mean_reversion_signal

def consensus(features, regime):
    votes = []

    votes.append(trend_following_signal(features))
    votes.append(breakout_signal(features))
    votes.append(mean_reversion_signal(features))

    score = sum(votes)

    # strict quality rule
    if regime == "TRENDING":
        return score >= 2
    elif regime == "RANGING":
        return score >= 2
    else:
        return score >= 3  # high volatility = stricter

