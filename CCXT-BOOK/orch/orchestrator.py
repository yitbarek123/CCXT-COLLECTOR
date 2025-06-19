import ccxt
import docker
import os

# Initialize Docker client (Docker must be installed inside the orchestrator container)
client = docker.from_env()

# Directory on the host where data will be stored
host_data_dir = "/data/ccxt-data-book/"  # Updated to use /data/ccxt-data-book

# Iterate over all exchanges in ccxt
for exchange_name in ccxt.exchanges:
    # Name the container based on the exchange, adding "book" in the container name
    container_name = f"{exchange_name}-ccxt-book-trade"

    # Create a specific directory for this exchange to store data
    exchange_data_dir = os.path.join(host_data_dir, exchange_name)
    os.makedirs(exchange_data_dir, exist_ok=True)  # Create directory on the host if it doesn't exist

    # Set environment variables
    env_vars = {
        'EXCHANGE_NAME': exchange_name
    }

    # Check if the container exists and remove it if it does
    try:
        existing_container = client.containers.get(container_name)
        print(f"Container {container_name} already exists. Removing it...")
        existing_container.stop()
        existing_container.remove()
    except docker.errors.NotFound:
        print(f"No existing container named {container_name}. Proceeding to create a new one.")

    # Start a new container with the specified environment variable and volume mount
    try:
        container = client.containers.run(
            image="collector-ccxt-book",  # Replace with your image name for fetching trades
            name=container_name,
            environment=env_vars,
            volumes={exchange_data_dir: {'bind': exchange_data_dir, 'mode': 'rw'}},  # Updated volume directory
            detach=True
        )
        print(f"Started container {container_name} for exchange {exchange_name}, writing data to {exchange_data_dir}")
    except Exception as e:
        print(f"Failed to start container for {exchange_name}: {e}")