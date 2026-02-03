import numpy as np

def trend_alignment(htf_trend, signal_type):
    return (htf_trend == "UP" and signal_type == "LONG") or \
           (htf_trend == "DOWN" and signal_type == "SHORT")

def momentum_confirmation(rsi, signal_type):
    if signal_type == "LONG":
        return rsi > 50 and rsi < 70
    else:
        return rsi < 50 and rsi > 30

def volatility_filter(atr, min_atr):
    return atr >= min_atr

def risk_reward_filter(entry, tp, sl, min_rr=2.5):
    rr = abs(tp - entry) / abs(entry - sl)
    return rr >= min_rr, rr

def confidence_filter(conf, threshold=0.75):
    return conf >= threshold

def compute_score(conf, rr, atr_norm):
    # weighted quality score
    return round((conf * 0.5 + rr * 0.3 + atr_norm * 0.2), 4)
