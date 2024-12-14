import polars as pl
from typing import List
import yaml
import os

class ParquetFiles:
    def __init__(self, parquet_data_dir: str = "parquet_files"):
        self.parquet_data_dir = parquet_data_dir

    @property
    def lazy_frame(self) -> pl.LazyFrame:
        """
        Lazy load all parquet files and enforce schema:
        Columns: Date, Ticker, Close, MarketCap.
        Missing columns are filled with None.
        """
        schema = ["Date", "Ticker", "Close", "MarketCap"]
        return (
            pl.scan_parquet(f"{self.parquet_data_dir}/**/*.parquet")
            .with_columns(
                pl.col("Date").cast(pl.Datetime)  # Ensure Date is a Datetime
            )
            .pipe(self._enforce_schema, schema=schema)
        )

    @staticmethod
    def _enforce_schema(lf: pl.LazyFrame, schema: List[str]) -> pl.LazyFrame:
        """
        Ensures that the LazyFrame conforms to the specified schema.
        Adds missing columns with default None values.
        """
        for col in schema:
            if col not in lf.schema:
                lf = lf.with_columns(pl.lit(None).alias(col))
        return lf.select(schema)  # Ensure correct column order


class CsvFiles:
    def __init__(self, csv_data_dir: str = "csv_files"):
        self.csv_data_dir = csv_data_dir

    @property
    def lazy_frame(self) -> pl.LazyFrame:
        """
        Lazy load all CSV files and enforce schema:
        Columns: Date, Ticker, Close, MarketCap.
        Missing columns are filled with None.
        """
        schema = ["Date", "Ticker", "Close", "MarketCap"]
        return (
            pl.scan_csv(f"{self.csv_data_dir}/**/*.csv")
            .with_columns(
                pl.col("Date").str.strptime(pl.Datetime, "%Y-%m-%d")  # Ensure Date is a Datetime
            )
            .pipe(self._enforce_schema, schema=schema)
        )

    @staticmethod
    def _enforce_schema(lf: pl.LazyFrame, schema: List[str]) -> pl.LazyFrame:
        """
        Ensures that the LazyFrame conforms to the specified schema.
        Adds missing columns with default None values.
        """
        for col in schema:
            if col not in lf.schema:
                lf = lf.with_columns(pl.lit(None).alias(col))
        return lf.select(schema)  # Ensure correct column order


class MarketData:
    """
    A class to handle market data stored in parquet and csv files using Polars LazyFrame.
    """
    def __init__(self, parquet_data_dir: str = "parquet_files", csv_data_dir: str = "csv_files", yaml_file: str = "currencies.yaml"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.yaml_file = os.path.join(base_dir, yaml_file)
        self.parquet_files = ParquetFiles(parquet_data_dir)
        self.csv_files = CsvFiles(csv_data_dir)
        self._lazy_frame = None
        self._currencies_frame = None

    @property
    def df(self) -> pl.LazyFrame:
        """
        LazyFrame property that loads and merges data from parquet and csv files.
        Ensures data is sorted by date (descending) and removes duplicates.
        Adjusts the MarketCap for currency tickers using multipliers from the YAML file.

        Returns:
            pl.LazyFrame: LazyFrame containing the merged market data
        """
        if self._lazy_frame is None:
            raw_data = pl.concat([
                self.parquet_files.lazy_frame,
                self.csv_files.lazy_frame
            ], how="diagonal")

            self._lazy_frame = (
                raw_data
                .join(self.currencies, on="Ticker", how="left")
                .with_columns(
                    pl.when(pl.col("Multiplier").is_not_null())
                    .then(pl.col("Close") * pl.col("Multiplier"))
                    .otherwise(pl.col("MarketCap"))
                    .cast(pl.Float64)
                    .alias("MarketCap")
                )
                .unique(subset=["Date", "Ticker", "MarketCap", "Close"])
                .sort(["Date"], descending=True)
                .select(["Date", "Ticker", "MarketCap", "Close"])
            )
        return self._lazy_frame

    @property
    def currencies(self) -> pl.LazyFrame:
        """
        LazyFrame property that loads ticker multipliers from a YAML file and 
        creates a mini dataframe with Ticker and Multiplier columns.
        
        Returns:
            pl.LazyFrame: LazyFrame containing the currencies and multipliers.
        """
        if self._currencies_frame is None:
            # Load YAML file and create a DataFrame
            with open(self.yaml_file, "r") as file:
                data = yaml.safe_load(file)

            # Convert YAML data into a list of dictionaries for Polars
            rows = [{"Ticker": ticker, "Multiplier": info["multiplier"]} for ticker, info in data["currencies"].items()]
            
            # Create a LazyFrame from the rows
            self._currencies_frame = pl.DataFrame(rows).lazy()

        return self._currencies_frame


Tickers = MarketData()