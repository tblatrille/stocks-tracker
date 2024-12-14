import yfinance as yf
import pandas as pd
import yaml
import os
from datetime import datetime

# Function to read tickers from YAML file
def read_tickers(yaml_file="tickers.yaml"):
    """
    Reads ticker symbols from a YAML file, resolving its path dynamically.

    Parameters:
        yaml_file (str): Name of the YAML file containing ticker symbols
    Returns:
        list: List of ticker symbols
    """
    # Resolve the base directory of the current script
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Full path to the YAML file
    full_path = os.path.join(base_dir, yaml_file)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"The file {yaml_file} was not found in {base_dir}")

    with open(full_path, 'r') as file:
        data = yaml.safe_load(file)
        return data['tickers']

def scrape_ticker_data(tickers, start_date=None, end_date=None, output_dir="parquet_files"):
    """
    Scrapes historical data with smart date handling and ticker partitioning.
    Data is partitioned by ticker and each file contains a specific date range.
    """
    os.makedirs(output_dir, exist_ok=True)
    end_date = datetime.now() if end_date is None else pd.to_datetime(end_date)
    
    for ticker in tickers:
        print(f"Processing {ticker}...")
        
        # Handle date logic per ticker
        ticker_start_date = start_date
        if ticker_start_date is None:
                ticker_start_date = datetime(2020, 1, 1)
        else:
            ticker_start_date = pd.to_datetime(ticker_start_date)
        
        # Skip if no new data needed
        if ticker_start_date >= end_date:
            print(f"No new data to fetch for {ticker}")
            continue
        
        # Create ticker-specific directory
        ticker_dir = os.path.join(output_dir, f"ticker={ticker}")
        os.makedirs(ticker_dir, exist_ok=True)
        
        # Format dates for filename
        file_name = f"data_{ticker_start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.parquet"
        output_file = os.path.join(ticker_dir, file_name)
        
        try:
            # Fetch historical stock data
            data = yf.download(ticker, start=ticker_start_date, end=end_date)
            
            if not data.empty:
                data.columns = [i[0] for i in data.columns]
                data["Ticker"] = ticker
                
                # Fetch shares outstanding for the ticker
                stock = yf.Ticker(ticker)
                shares_outstanding = stock.info.get("sharesOutstanding", None)
                
                if shares_outstanding:
                    # Calculate market cap for each row
                    data["MarketCap"] = data["Close"] * float(shares_outstanding)
                else:
                    data["MarketCap"] = data["Close"]
                # Save individual ticker data
                data.to_parquet(output_file, engine="pyarrow")
                print(f"Data for {ticker} from {ticker_start_date.date()} to {end_date.date()} saved to {output_file}")
        except Exception as e:
            print(f"Failed to fetch data for {ticker}: {e}")

# Example usage
if __name__ == "__main__":
    tickers = read_tickers()
    scrape_ticker_data(tickers=tickers, start_date="1900-01-01", end_date="2024-12-13")
