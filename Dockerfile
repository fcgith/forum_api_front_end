# Use the official Python slim image
FROM python:3.12.5-slim

# Set the working directory
WORKDIR /app

# Install system dependencies for MariaDB Connector/C
RUN apt-get update && apt-get install -y \
    libmariadb-dev \
    gcc \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project directory
COPY . .

# Command to run the application (adjust as needed)
CMD ["python", "main.py"]