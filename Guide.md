# 📘 Nexus Operations Guide

### 1. Monitoring the Engine
To check if the bot is running correctly:
1. Go to your GitHub Repository.
2. Click the **Actions** tab.
3. Click on the latest **Nexus Engine Runner** workflow.
4. Expand the **Run Engine** step to see real-time logs of the market scan.

### 2. Understanding Discord Alerts
- **🚀 NEXUS SIGNAL:** A high-probability setup was found. These include Entry, Take Profit, and Stop Loss.
- **🛡️ Patience Message:** The engine ran successfully but did not find a setup that met the `MIN_CONFIDENCE` threshold. 
  *Note: If you don't receive this message at the top of the hour, the GitHub Action failed to trigger.*

### 3. Using the Emergency Kill-Switch
If you need to stop the bot immediately (e.g., during a Black Swan event):
1. Navigate to **Settings > Secrets and variables > Actions**.
2. Find `NEXUS_ACTIVE`.
3. Change the value from `TRUE` to `FALSE`.
4. The next hourly run will log "🛑 KILL-SWITCH DETECTED" and exit immediately.

### 4. Technical Specifications
- **Risk/Reward:** 1:3 (0.5% SL / 1.5% TP).
- **Exchange:** Gate.io (via CCXT).
- **Timeframe:** 1-Hour intervals (Optimized for GitHub Free Tier).
