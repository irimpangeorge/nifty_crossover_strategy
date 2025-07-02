import pandas as pd
import yfinance as yf
import pandas_ta as ta
import streamlit as st
from dhanhq import dhanhq
from datetime import datetime

CLIENT_ID = "1000582912"
ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzUzNTg5MTU0LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTAwMDU4MjkxMiJ9.DlgegxnfDMVZQGYN6_TRzYNnLPiKfHxW7OMRRM5TfhYSflB9GgWSpvmnJN92UwlUNu2ikRZziq6rOY_BdFTTJQ"
dhan = dhanhq(CLIENT_ID, ACCESS_TOKEN)


# === Config ===
SYMBOL = "INFY"
EXCHANGE = dhan.NSE  # NSE Equity
QUANTITY = 10  # number of shares to trade


# === Get security_id for INFY ===
@st.cache_data
def get_security_id(symbol):
    result = dhan.search_scrips(EXCHANGE, symbol)
    return result[0]['security_id']

security_id = 1594

# Fetch market data
def fetch_data():
    df = yf.download('^NSEI', period="5d", interval="15m", group_by="column")
    df.columns = ['Close', 'High', 'Low', 'Open', 'Volume']
    df.index = df.index.tz_convert("Asia/Kolkata")
    df.dropna(inplace=True)
    df["EMA_5"] = ta.ema(df["Close"], length=5)
    df["EMA_9"] = ta.ema(df["Close"], length=9)
    return df

# Place order
def place_order(order_type):
    order = dhan.place_order(
        security_id=security_id,
        exchange_segment=EXCHANGE,
        transaction_type=getattr(dhan, order_type),
        quantity=QUANTITY,
        order_type=dhan.MARKET,
        product_type=dhan.INTRADAY,
        price=0
    )
    st.success(f"{datetime.now()} → {order_type} order placed successfully!")

# Streamlit UI
st.title("📊 EMA 5/9 Crossover Trading")

df = fetch_data()
latest = df.iloc[-1]
previous = df.iloc[-2]

# Show latest signal
signal = ""
if previous.EMA_5 < previous.EMA_9 and latest.EMA_5 > latest.EMA_9:
    signal = "Golden Cross 📈 — Buy Signal"
elif previous.EMA_5 > previous.EMA_9 and latest.EMA_5 < latest.EMA_9:
    signal = "Death Cross 📉 — Sell Signal"
else:
    signal = "➖ No Signal"

st.subheader(f"Latest Signal: {signal}")

# Manual trading buttons

# Optional: Show last 30 records in a table
with st.expander("📈 Show line chart"):
    st.line_chart(df[["EMA_5", "EMA_9"]].tail(30))

# Optional: Show last 30 records in a table
with st.expander("📊 Show raw data (IST timings)"):
    st.dataframe(df.tail(30))


if st.button("Refresh Data"):
    st.experimental_rerun()
