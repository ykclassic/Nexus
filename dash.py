import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
from engine.config import DB_PATH

st.set_page_config(page_title="Nexus Command Centre", layout="wide")

def get_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM signals ORDER BY created_at DESC", conn)
    conn.close()
    return df

st.title("🛡️ Nexus Intelligence Dashboard")
st.write("Real-time Trade Monitoring & Signal Analytics")

data = get_data()

if not data.empty:
    # Top Stats
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Signals", len(data))
    col2.metric("Avg Confidence", f"{round(data['confidence'].mean(), 2)}%")
    col3.metric("Last Update", data['created_at'].iloc[0])

    # Signal Table
    st.subheader("Recent Signals")
    st.dataframe(data, use_container_width=True)

    # Confidence Chart
    st.subheader("Signal Distribution")
    fig = go.Figure(data=[go.Histogram(x=data['confidence'], nbinsx=20, marker_color='#636EFA')])
    fig.update_layout(title="Confidence Frequency", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Waiting for first signal to be recorded in database...")
