"""
NEXUS TRADE LIFECYCLE ENGINE
Responsible for creating, validating, scoring, and managing signals.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Optional
from engine.db import get_connection
from engine.config import MIN_CONFIDENCE


@dataclass
class TradeSignal:
    asset: str
    timeframe: str
    direction: str  # LONG / SHORT
    confidence: float
    price: float
    strategy: str
    timestamp: str


def validate_signal(signal: TradeSignal) -> bool:
    """Validate signal quality and constraints."""
    if signal.direction not in ["LONG", "SHORT"]:
        return False
    if signal.confidence < MIN_CONFIDENCE:
        return False
    if signal.price <= 0:
        return False
    return True


def score_signal(signal: TradeSignal) -> float:
    """
    Advanced scoring logic.
    You can expand this with AI, volatility, regime, etc.
    """
    base_score = signal.confidence

    # Strategy weighting
    strategy_weights = {
        "trend_following": 1.05,
        "mean_reversion": 1.02,
        "breakout": 1.08,
        "liquidity_sweep": 1.1,
        "nexus_alpha": 1.15,  # new custom strategy
    }

    weight = strategy_weights.get(signal.strategy, 1.0)
    return round(base_score * weight, 4)


def persist_signal(signal: TradeSignal) -> None:
    """Save signal to database."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO signals (asset, timeframe, signal, confidence, price, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        signal.asset,
        signal.timeframe,
        signal.direction,
        signal.confidence,
        signal.price,
        signal.timestamp
    ))

    conn.commit()
    conn.close()


def create_signal(
    asset: str,
    timeframe: str,
    direction: str,
    confidence: float,
    price: float,
    strategy: str = "nexus_alpha"
) -> Optional[Dict]:
    """
    Main entry point used by runner.py
    """

    signal = TradeSignal(
        asset=asset,
        timeframe=timeframe,
        direction=direction,
        confidence=confidence,
        price=price,
        strategy=strategy,
        timestamp=datetime.utcnow().isoformat()
    )

    if not validate_signal(signal):
        return None

    final_score = score_signal(signal)
    signal.confidence = final_score

    persist_signal(signal)

    return asdict(signal)
