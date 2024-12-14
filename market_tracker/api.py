from fastapi import FastAPI, Query
from datetime import datetime
from typing import List, Optional
import polars as pl
from market_tracker.data import Tickers
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Market Data API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/tickers")
async def get_available_tickers() -> List[str]:
    """
    Get list of all available tickers.
    """
    unique_tickers = (
        Tickers.df
        .select("Ticker")
        .unique()
        .sort("Ticker")
        .collect()
    )
    
    return unique_tickers["Ticker"].to_list()

@app.get("/prices/{ticker}")
async def get_prices(
    ticker: str,
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format")
) -> List[dict]:
    """
    Get closing prices for a specific ticker within the date range.
    Returns an array of objects containing date and closing price.
    """
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    df = (
        Tickers.df.filter(
            (pl.col("Ticker") == ticker) &
            (pl.col("Date") >= start_date) &
            (pl.col("Date") <= end_date)
        ).select("Date", "Close").collect()
    )
    
    return [
        {"date": row["Date"].strftime("%Y-%m-%d"), "price": row["Close"]}
        for row in df.to_dicts()
    ]

@app.get("/date-range")
async def get_date_range():
    """
    Get the minimum and maximum dates available in the dataset.
    """
    date_range = (
        Tickers.df
        .select(
            min_date=pl.col("Date").min(),
            max_date=pl.col("Date").max()
        )
        .collect()
        .to_dicts()[0]
    )
    
    return {
        "min_date": date_range["min_date"].strftime("%Y-%m-%d"),
        "max_date": date_range["max_date"].strftime("%Y-%m-%d")
    }

@app.get("/ratio/{ticker1}/{ticker2}")
async def get_ratio(
    ticker1: str,
    ticker2: str,
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format")
) -> List[dict]:
    """
    Get the price ratio between two tickers (ticker1/ticker2) within the date range.
    Returns an array of objects containing date and ratio.
    """
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    
    ratio_df = (
        Tickers.df.filter(pl.col("Ticker") == ticker1)
        .join(
            Tickers.df.filter(pl.col("Ticker") == ticker2),
            on="Date",
            how="inner"
        )
        .filter(
            (pl.col("Date") >= start_date) &
            (pl.col("Date") <= end_date)
        )
        .with_columns([
            ((pl.col("MarketCap") / pl.col("MarketCap_right")).round(3).alias("ratio"))
        ])
        .select(["Date", "ratio"])
        .collect()
    )
    
    return [
        {"date": row["Date"].strftime("%Y-%m-%d"), "ratio": row["ratio"]}
        for row in ratio_df.to_dicts()
    ]

@app.get("/marketcap")
async def get_marketcap(
    ticker: Optional[str] = Query(None, description="Ticker symbol to filter by"),
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format")
) -> List[dict]:
    """
    Get adjusted MarketCap for all tickers or a specific ticker within the date range.
    If the ticker is a currency, MarketCap is recalculated as Multiplier * Close.
    Returns an array of objects containing date and adjusted market cap.
    """
    # Parse start and end dates
    start_date = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
    end_date = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None

    # Filter data by date range
    data_filtered = Tickers.df.filter(
        (pl.col("Date") >= start_date) if start_date else pl.lit(True)
    ).filter(
        (pl.col("Date") <= end_date) if end_date else pl.lit(True)
    )

    # Apply ticker filter if provided
    if ticker:
        data_filtered = data_filtered.filter(pl.col("Ticker") == ticker)
    # Collect and return the adjusted market cap data
    result = data_filtered.select(["Date", "MarketCap"]).collect()
    
    return [
        {
            "date": row["Date"].strftime("%Y-%m-%d"),
            "market_cap": row["MarketCap"]
        }
        for row in result.to_dicts()
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        reload_includes=["*.py", "*.html", "*.yaml"],  # Watch these file patterns
        reload_excludes=[".*", ".py[cod]", "*.log"],  # Ignore these patterns
    )
