import os
from pathlib import Path
import polars as pl
import yaml

class ParquetFiles:
    def __init__(self, base_dir: str, parquet_data_dir: str = "parquet_files"):
        self.parquet_data_dir = os.path.join(base_dir, parquet_data_dir)

    @property
    def lazy_frame(self) -> pl.LazyFrame:
        """
        Lazy load all parquet files.
        """
        return (
            pl.scan_parquet(f"{self.parquet_data_dir}/**/*.parquet")
            .with_columns(
                pl.col("Date").cast(pl.Date)  # Cast to Date (day precision)
            )
        )


class CsvFiles:
    def __init__(self, base_dir: str, csv_data_dir: str = "csv_files"):
        self.csv_data_dir = os.path.join(base_dir, csv_data_dir)

    @property
    def lazy_frame(self) -> pl.LazyFrame:
        """
        Lazy load all CSV files and add a 'Ticker' column based on the filename.
        """
        csv_files = Path(self.csv_data_dir).rglob("*.csv")
        frames = []
        for csv_file in list(csv_files):
            ticker = csv_file.stem
            df = (
                pl.scan_csv(csv_file)
                .with_columns(
                    pl.lit(ticker).alias("Ticker"),  # Add the Ticker column
                    pl.col("Date").str.strptime(pl.Date, "%Y-%m-%d")  # Convert Date to Date type (day precision)
                )
            )
            frames.append(df)
        return pl.concat(frames) if frames else pl.DataFrame()  # Concatenate all frames


class MarketData:
    """
    A class to handle market data stored in parquet and csv files using Polars LazyFrame.
    """
    def __init__(self, base_dir: str, parquet_data_dir: str = "parquet_files", csv_data_dir: str = "csv_files", yaml_file: str = "currencies.yaml"):
        self.parquet_files = ParquetFiles(base_dir, parquet_data_dir)
        self.csv_files = CsvFiles(base_dir, csv_data_dir)
        self._lazy_frame = None
        self._currencies_frame = None
        base_dir_ = os.path.dirname(os.path.abspath(__file__))
        self.yaml_file = os.path.join(base_dir_, yaml_file)

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

# Example usage
base_dir = os.getcwd()  # Get the current working directory
Tickers = MarketData(base_dir)