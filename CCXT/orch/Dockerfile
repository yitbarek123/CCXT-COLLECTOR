# Dockerfile for Orchestrator
FROM python:3.9-slim

# Install Docker inside the container
RUN apt-get update && apt-get install -y docker.io

# Install required Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the orchestrator script
COPY . /app/

# Set the working directory
WORKDIR /app

# Run the orchestrator script
CMD ["python3", "orchestrator.py"]