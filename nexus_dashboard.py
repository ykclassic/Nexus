import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

DB_PATH = "data/trading.db"

st.set_page_config(page_title="Nexus Trading Dashboard", layout="wide")

st.title("🚀 Nexus Trading Engine Dashboard")
st.caption("Live monitoring of signals, trades, and engine activity")

if not os.path.exists(DB_PATH):
    st.error("Database not found. Engine has not run yet.")
    st.stop()

conn = sqlite3.connect(DB_PATH)

# ---------- LOAD DATA ----------
signals_df = pd.read_sql_query("SELECT * FROM signals ORDER BY created_at DESC", conn)

# ---------- METRICS ----------
col1, col2, col3, col4 = st.columns(4)

open_trades = len(signals_df[signals_df['status'] == 'OPEN'])
closed_trades = len(signals_df[signals_df['status'].isin(['TP','SL'])])

win_trades = len(signals_df[signals_df['status'] == 'TP'])
loss_trades = len(signals_df[signals_df['status'] == 'SL'])

win_rate = (win_trades / closed_trades * 100) if closed_trades > 0 else 0

col1.metric("Open Trades", open_trades)
col2.metric("Closed Trades", closed_trades)
col3.metric("Win Rate (%)", f"{win_rate:.2f}")
col4.metric("Total Signals", len(signals_df))

st.divider()

# ---------- LIVE SIGNALS ----------
st.subheader("📈 Live Open Signals")
open_df = signals_df[signals_df['status'] == 'OPEN']

if open_df.empty:
    st.info("No open signals")
else:
    st.dataframe(open_df[[
        'symbol','signal_type','entry','tp','sl','confidence','created_at'
    ]], use_container_width=True)

# ---------- CLOSED TRADES ----------
st.subheader("📊 Closed Trades")
closed_df = signals_df[signals_df['status'].isin(['TP','SL'])]

if closed_df.empty:
    st.info("No closed trades yet")
else:
    st.dataframe(closed_df[[
        'symbol','signal_type','entry','exit_price','result','status','exit_time'
    ]], use_container_width=True)

# ---------- PERFORMANCE ----------
st.subheader("💰 Performance Analytics")

if not closed_df.empty:
    pnl_series = closed_df['result'].cumsum()
    st.line_chart(pnl_series)
else:
    st.info("No performance data yet")

# ---------- ENGINE STATUS ----------
st.subheader("⚙️ Engine Status")

st.write("Last update:", datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"))
st.write("Database path:", DB_PATH)

conn.close()
