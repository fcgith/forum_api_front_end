# Use the official Python slim image
FROM python:3.12.5-slim

# Set the working directory
WORKDIR /app

# Install system dependencies for MariaDB Connector/C and git
RUN apt-get update && apt-get install -y \
    libmariadb-dev \
    gcc \
    pkg-config \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up SSH for Git
RUN mkdir -p /root/.ssh && ssh-keyscan github.com >> /root/.ssh/known_hosts
COPY id_rsa /root/.ssh/id_rsa
RUN chmod 600 /root/.ssh/id_rsa

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project directory
COPY . .

# Copy the update script
COPY update_and_run.sh .

# Ensure the script has executable permissions
RUN chmod +x update_and_run.sh

# Command to run the update script
CMD ["./update_and_run.sh"]