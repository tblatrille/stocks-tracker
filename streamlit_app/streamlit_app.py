import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import datetime

# API base URL
API_URL = "http://localhost:8000"

# Set up the page
st.set_page_config(page_title="", layout="wide")

# Sidebar setup
view_type = st.sidebar.radio("", ["Prices", "MarketCap", "Ratio"])

# Get available tickers
tickers = requests.get(f"{API_URL}/tickers").json()
date_range = requests.get(f"{API_URL}/date-range").json()

# Date range selector
start_date = st.sidebar.date_input(
    "Start Date",
    datetime.strptime(date_range["min_date"], "%Y-%m-%d"),
    min_value=datetime.strptime(date_range["min_date"], "%Y-%m-%d"),
    max_value=datetime.strptime(date_range["max_date"], "%Y-%m-%d")
)
end_date = st.sidebar.date_input(
    "End Date",
    datetime.strptime(date_range["max_date"], "%Y-%m-%d"),
    min_value=datetime.strptime(date_range["min_date"], "%Y-%m-%d"),
    max_value=datetime.strptime(date_range["max_date"], "%Y-%m-%d")
)

if view_type == "Prices":
    # Single ticker selector for prices
    ticker = st.sidebar.selectbox("Select Ticker", tickers)
    
    if st.sidebar.button("Fetch Data"):
        # Get price data
        response = requests.get(
            f"{API_URL}/prices/{ticker}",
            params={
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d")
            }
        )
        data = response.json()
        
        # Create plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[item["date"] for item in data],
            y=[item["price"] for item in data],
            mode='lines',
            name=ticker
        ))
        
        fig.update_layout(
            title=f"{ticker} Price History",
            xaxis_title="Date",
            yaxis_title="Price",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)

elif view_type == "Ratio":
    # Two ticker selectors for ratio
    ticker1 = st.sidebar.selectbox("First Ticker", tickers, key="ticker1")
    ticker2 = st.sidebar.selectbox("Second Ticker", tickers, key="ticker2")
    
    if st.sidebar.button("Fetch Data"):
        # Get ratio data
        response = requests.get(
            f"{API_URL}/ratio/{ticker1}/{ticker2}",
            params={
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d")
            }
        )
        data = response.json()
        
        # Create plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[item["date"] for item in data],
            y=[item["ratio"] for item in data],
            mode='lines',
            name=f'{ticker1}/{ticker2} Ratio'
        ))
        
        fig.update_layout(
            title=f"Price Ratio: {ticker1}/{ticker2}",
            xaxis_title="Date",
            yaxis_title="Ratio",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)

elif view_type == "MarketCap":
    # Single ticker selector for MarketCap
    ticker = st.sidebar.selectbox("Select Ticker", tickers)
    
    if st.sidebar.button("Fetch Data"):
        # Get market cap data
        response = requests.get(
            f"{API_URL}/marketcap",
            params={
                "ticker": ticker,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d")
            }
        )
        data = response.json()
        # Create plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[item["date"] for item in data],
            y=[item["market_cap"] for item in data],
            mode='lines',
            name=f"{ticker} MarketCap"
        ))
        
        fig.update_layout(
            title=f"{ticker} MarketCap",
            xaxis_title="Date",
            yaxis_title="MarketCap",
            hovermode='x unified',
            yaxis=dict(type='log')
        )
        
        st.plotly_chart(fig, use_container_width=True)