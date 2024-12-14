# Base Python image
FROM python:3.13.1-slim

# Set working directory
WORKDIR /app

# Copy Streamlit app files
COPY streamlit_app /app

# Upgrade pip
RUN python -m pip install --no-cache-dir --upgrade pip

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Expose Streamlit port internally
EXPOSE 8501

# Start Streamlit
CMD ["streamlit", "run", "streamlit_app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]