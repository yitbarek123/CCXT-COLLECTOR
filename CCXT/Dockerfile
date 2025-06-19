# Step 1: Use the official Python image from Docker Hub
FROM python:3.9-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy the requirements file into the container
COPY requirements.txt .

# Step 4: Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the Python code into the container
COPY . .

# Step 6: Set environment variable placeholder
# (Optional) This is not necessary but can serve as a default or reminder of expected variables.
# ENV EXCHANGE_NAME=

# Step 7: Define the command to run the Python script
# Use "python3" with environment variables passed at runtime
CMD ["python3", "collector.py"]
