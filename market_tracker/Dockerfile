# Base Python image
FROM python:slim

# Set working directory
WORKDIR /app

# Copy FastAPI app files and the parquet_files directory
COPY market_tracker /app
COPY parquet_files /app/parquet_files
COPY csv_files /app/csv_files

# Upgrade pip
RUN python -m pip install --no-cache-dir --upgrade pip
# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Expose FastAPI port internally
EXPOSE 8000

# Start FastAPI
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]