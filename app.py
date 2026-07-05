import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests

# 1. Page Settings
st.set_page_config(page_title="Real-Time Stock Dashboard", page_icon="📈", layout="wide")
st.title("📈 Real-Time Stock Market Dashboard")

# Fix: Prevent Yahoo Finance from blocking requests
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

# 2. Sidebar Configuration
st.sidebar.header("Dashboard Settings")
ticker_list = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA"]
selected_ticker = st.sidebar.selectbox("Select Stock Ticker", ticker_list)

custom_ticker = st.sidebar.text_input("Or enter custom ticker (e.g., AMD):").upper()
if custom_ticker:
    selected_ticker = custom_ticker

time_window = st.sidebar.selectbox(
    "Select Time Interval",
    options=["1 Day (1m intervals)", "5 Days (5m intervals)", "1 Month (1d intervals)"]
)

# Fetch Data
@st.cache_data(ttl=15)
def fetch_stock_data(ticker, window):
    try:
        stock = yf.Ticker(ticker, session=session)
        if window == "1 Day (1m intervals)":
            df = stock.history(period="1d", interval="1m")
        elif window == "5 Days (5m intervals)":
            df = stock.history(period="5d", interval="5m")
        else:
            df = stock.history(period="1mo", interval="1d")
        
        try:
            info = stock.info
        except:
            info = {}
            
        return df, info
    except:
        return None, None

df, info = fetch_stock_data(selected_ticker, time_window)

# 3. Render Dashboard Layout
if df is not None and not df.empty:
    current_price = df['Close'].iloc[-1]
    prev_close = info.get('previousClose') if info and info.get('previousClose') else df['Close'].iloc[0]
    company_name = info.get('longName') if info and info.get('longName') else selected_ticker
    
    price_change = current_price - prev_close
    pct_change = (price_change / prev_close) * 100

    # Layout Metrics
    st.subheader(f"{company_name} ({selected_ticker})")
    c1, c2, c3 = st.columns(3)
    c1.metric("Current Price", f"${current_price:,.2f}", f"{price_change:+.2f} ({pct_change:+.2f}%)")
    c2.metric("Daily High", f"${df['High'].max():,.2f}")
    c3.metric("Daily Volume", f"{df['Volume'].iloc[-1]:,}")

    # Layout Chart
    fig = go.Figure(data=[go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']
    )])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=400)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ Fetching data from Yahoo Finance... Try changing tickers if this stays blank.")