# Market Tracker Project

## Overview
The **Market Tracker** is a containerized application for tracking financial data, visualizing stock prices, market caps, and price ratios. It consists of a **FastAPI** backend, a **Streamlit** frontend, and a scarper for fetching data.

---

## Project Structure

```
.
├── README.md                   # Project documentation
├── docker-compose.yml          # Docker Compose configuration
├── market_tracker/             # Backend FastAPI application
│   ├── Dockerfile              # Dockerfile for FastAPI
│   ├── api.py                  # Main API implementation
│   ├── scraper.py              # Data scraping script
│   ├── query_logic.py          # Backend logic for queries
│   ├── tickers.yaml            # YAML file with ticker symbols
│   ├── requirements.txt        # Backend dependencies
├── streamlit_app/              # Frontend Streamlit application
│   ├── Dockerfile              # Dockerfile for Streamlit
│   ├── streamlit_app.py        # Main Streamlit app
│   ├── requirements.txt        # Frontend dependencies
├── parquet_files/              # Directory for Parquet files (fetched data)
├── csv_files/                  # Directory for CSV files
├── nginx/                      # Configuration for NGINX reverse proxy
│   └── nginx.conf              # NGINX configuration file
```

---

## Features

1. **FastAPI Backend:**
   - Provides API endpoints for querying stock prices, ratios, market caps, etc.
   - Built with modular and reusable Python logic.

2. **Streamlit Frontend:**
   - Visualizes data fetched from the backend in an interactive dashboard.
   - Provides views for prices, ratios, and market caps.

3. **Scraper**
   - Scrapes and update stock data from Yahoo Finance.
   - Saves data in Parquet format for efficient querying.

4. **Containerized with Docker Compose:**
   - Manages all services (FastAPI, Streamlit, and scraper) using Docker Compose.
   - Uses NGINX as a reverse proxy for the frontend.

---

## Installation and Usage

### 1. Clone the Repository
```bash
git clone <repository_url>
cd tracker
```

### 2. Build Docker Images
Build the Docker images for all services:
```bash
docker-compose build --no-cache
```

### 3. Start Services
Start all services in detached mode:
```bash
docker-compose up -d
```

### 4. Access the Application
- **Streamlit Frontend:** [http://localhost:80](http://localhost:80)
- **FastAPI Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Data Scraper

The `scraper.py` script:
- Scrapes historical stock data from Yahoo Finance.
- Saves data to `parquet_files/` in a partitioned format (e.g., `ticker=AAPL`).

You can manually trigger the scraper by running:
```bash
docker exec -it <container_id> python /app/scraper.py
```

Logs are saved in `/var/log/cron/scraper.log`.

---

## API Endpoints

- **Available Tickers:**
  ```
  GET /tickers
  ```
- **Prices:**
  ```
  GET /prices/{ticker}?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
  ```
- **Market Cap:**
  ```
  GET /marketcap?ticker={ticker}&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
  ```
- **Price Ratio:**
  ```
  GET /ratio/{ticker1}/{ticker2}?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
  ```

For detailed API docs, visit [http://localhost:8000/docs](http://localhost:8000/docs).

---

## Frontend Features

The Streamlit app provides:
- **Price History:** Interactive charts of stock price data.
- **Market Cap:** Visualization of market capitalization over time.
- **Price Ratios:** Comparisons between two stocks.

---

## Configuration

### 1. Add New Tickers
Add tickers to `market_tracker/tickers.yaml`:
```yaml
tickers:
  - AAPL
  - MSFT
  - TSLA
```

### 2. Adjust NGINX Configuration
The `nginx/nginx.conf` file routes requests between Streamlit and FastAPI.

---

## Troubleshooting

- **Check Container Logs:**
  ```bash
  docker logs <container_id>
  ```

- **Restart Services:**
  ```bash
  docker-compose restart
  ```

- **Remove Stopped Containers:**
  ```bash
  docker-compose down
  ```
