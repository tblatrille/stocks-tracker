import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import datetime
import os

# API base URL
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Set up the page
st.set_page_config(page_title="", layout="wide", page_icon=":rocket:")

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
    # Multiselect for prices
    selected_tickers = st.sidebar.multiselect("Select Tickers", tickers, default=tickers[:1])
    
    if selected_tickers:  # Automatically fetch data if tickers are selected
        fig = go.Figure()
        
        for ticker in selected_tickers:
            # Get price data
            response = requests.get(
                f"{API_URL}/prices/{ticker}",
                params={
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d")
                }
            )
            data = response.json()
            
            # Add ticker data to the plot
            fig.add_trace(go.Scatter(
                x=[item["date"] for item in data],
                y=[item["price"] for item in data],
                mode='lines',
                name=ticker
            ))
        
        fig.update_layout(
            title="Price History",
            xaxis_title="Date",
            yaxis_title="Price",
            hovermode='x unified',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False)
        )
        
        st.plotly_chart(fig, use_container_width=True)

elif view_type == "Ratio":
    # Multiselect for ratio (restricted to exactly two tickers)
    selected_tickers = st.sidebar.multiselect("Select Two Tickers for Ratio", tickers, default=tickers[:2])
    
    if len(selected_tickers) == 2:  # Automatically fetch data if exactly two tickers are selected
        ticker1, ticker2 = selected_tickers
        
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
            hovermode='x unified',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Please select exactly two tickers for the Ratio view.")

elif view_type == "MarketCap":
    # Multiselect for MarketCap
    selected_tickers = st.sidebar.multiselect("Select Tickers", tickers, default=tickers[:1])
    
    if selected_tickers:  # Automatically fetch data if tickers are selected
        fig = go.Figure()
        
        for ticker in selected_tickers:
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
            
            # Add ticker data to the plot
            fig.add_trace(go.Scatter(
                x=[item["date"] for item in data],
                y=[item["market_cap"] for item in data],
                mode='lines',
                name=f"{ticker}"
            ))
        
        fig.update_layout(
            title="MarketCap History",
            xaxis_title="Date",
            yaxis_title="MarketCap",
            hovermode='x unified',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False)
        )
        
        st.plotly_chart(fig, use_container_width=True)