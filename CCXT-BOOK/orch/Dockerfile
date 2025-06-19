# Dockerfile for Orchestrator
FROM python:3.9-slim

# Install necessary packages
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y docker.io

# Install Docker SDK for Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install docker

# Copy the orchestrator script
COPY . /app/

# Set the working directory
WORKDIR /app

# Run the orchestrator script
CMD ["python3", "orchestrator.py"]
