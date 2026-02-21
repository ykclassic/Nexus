# 🚀 Nexus Elite Engine v2.0

Nexus Elite is a multi-threaded market scanner designed to identify high-probability **Trend + Liquidity Sweep** setups. It operates as an automated daemon via GitHub Actions, delivering real-time signals directly to Discord.

## 🛠 Features
- **Smart Scanning:** Uses 5/20 MA trend filtering combined with 10-period liquidity sweep detection.
- **Multi-threaded:** Scans multiple symbols simultaneously using `ThreadPoolExecutor`.
- **Freshness Guard:** Automatically discards stale market data (older than 15 mins) to prevent ghost trades.
- **Heartbeat System:** Dispatches a "Patience" notification if no signals meet the confidence threshold.
- **Emergency Kill-Switch:** Pause all operations instantly via GitHub Secrets without touching the code.
- **Persistence:** All signals are logged to a local SQLite database (`trading.db`).

## 📂 Project Structure
```text
├── trainer_daemon.py      # Entry point (Bootstrap)
├── data/
│   └── trading.db         # SQLite Database (Auto-generated)
├── engine/
│   ├── runner.py          # Core Logic & Orchestration
│   ├── config.py          # Symbols, Timeframes, & Thresholds
│   ├── db.py              # Database initialization & Connections
│   ├── discord_alert.py   # Webhook integration
│   ├── elite_logger.py    # Event & Error logging
│   └── intelligence/
│       └── signal_scoring.py # Quantitative confidence scoring
└── .github/workflows/
    └── main.yml           # GitHub Actions Automation (Hourly)
