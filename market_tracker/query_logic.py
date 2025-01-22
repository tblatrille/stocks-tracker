from datetime import datetime
from typing import List, Optional
import polars as pl
from data import Tickers

# Core function: Get available tickers
def get_available_tickers() -> List[str]:
    unique_tickers = (
        Tickers.df
        .select("Ticker")
        .unique()
        .sort("Ticker")
        .collect()
    )
    return unique_tickers["Ticker"].to_list()

# Core function: Get prices
def get_prices(
    ticker: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[dict]:
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

# Core function: Get date range
def get_date_range():
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

# Core function: Get ratio
def get_ratio(
    ticker1: str,
    ticker2: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[dict]:
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
            ((pl.col("Close") / pl.col("Close_right")).round(3).alias("ratio"))
        ])
        .select(["Date", "ratio"])
        .collect()
    )
    return [
        {"date": row["Date"].strftime("%Y-%m-%d"), "ratio": row["ratio"]}
        for row in ratio_df.to_dicts()
    ]

# Core function: Get market cap
def get_marketcap(
    ticker: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[dict]:
    start_date = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
    end_date = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
    data_filtered = Tickers.df.filter(
        (pl.col("Date") >= start_date) if start_date else pl.lit(True)
    ).filter(
        (pl.col("Date") <= end_date) if end_date else pl.lit(True)
    )
    if ticker:
        data_filtered = data_filtered.filter(pl.col("Ticker") == ticker)
    result = data_filtered.select(["Date", "MarketCap"]).collect()
    return [
        {
            "date": row["Date"].strftime("%Y-%m-%d"),
            "market_cap": row["MarketCap"]
        }
        for row in result.to_dicts()
    ]