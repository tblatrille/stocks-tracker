from fastapi import FastAPI, Query
from typing import List, Optional
from query_logic import (
    get_available_tickers,
    get_prices,
    get_date_range,
    get_ratio,
    get_marketcap,
)

app = FastAPI(title="Market Data API")

@app.get("/tickers")
async def available_tickers() -> List[str]:
    """
    API endpoint: Get all available tickers.
    """
    return get_available_tickers()

@app.get("/prices/{ticker}")
async def prices(
    ticker: str,
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format")
) -> List[dict]:
    """
    API endpoint: Get prices for a ticker in a date range.
    """
    return get_prices(ticker, start_date, end_date)

@app.get("/date-range")
async def date_range() -> dict:
    """
    API endpoint: Get the date range of available data.
    """
    return get_date_range()

@app.get("/ratio/{ticker1}/{ticker2}")
async def ratio(
    ticker1: str,
    ticker2: str,
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format")
) -> List[dict]:
    """
    API endpoint: Get price ratio between two tickers.
    """
    return get_ratio(ticker1, ticker2, start_date, end_date)

@app.get("/marketcap")
async def marketcap(
    ticker: Optional[str] = Query(None, description="Ticker symbol to filter by"),
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format")
) -> List[dict]:
    """
    API endpoint: Get market cap for all or a specific ticker.
    """
    return get_marketcap(ticker, start_date, end_date)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0", 
        port=8051, 
        reload=True,
        reload_includes=["*.py", "*.html", "*.yaml"],  # Watch these file patterns
        reload_excludes=[".*", ".py[cod]", "*.log"],  # Ignore these patterns
    )
