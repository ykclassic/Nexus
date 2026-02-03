from engine.filters import *

def approve_signal(data):
    gates = 0
    reasons = []

    # Gate 1: Trend
    if trend_alignment(data["trend"], data["signal_type"]):
        gates += 1
    else:
        reasons.append("Trend misalignment")

    # Gate 2: Momentum
    if momentum_confirmation(data["rsi"], data["signal_type"]):
        gates += 1
    else:
        reasons.append("Weak momentum")

    # Gate 3: Volatility
    if volatility_filter(data["atr"], data["min_atr"]):
        gates += 1
    else:
        reasons.append("Low volatility")

    # Gate 4: Risk-Reward
    rr_ok, rr = risk_reward_filter(data["entry"], data["tp"], data["sl"])
    if rr_ok:
        gates += 1
    else:
        reasons.append("Low RR")

    # Gate 5: Confidence
    if confidence_filter(data["confidence"]):
        gates += 1
    else:
        reasons.append("Low confidence")

    approved = gates == 5
    score = compute_score(data["confidence"], rr, data["atr_norm"])

    return approved, gates, rr, score, ", ".join(reasons)
