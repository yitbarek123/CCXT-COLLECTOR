import docker

# Initialize Docker client
client = docker.from_env()

# Define a unique identifier for your containers
identifier = "-ccxt-trade"

# List all containers and filter those with the identifier
containers_to_remove = [container for container in client.containers.list(all=True) if identifier in container.name]

# Stop and remove each container
for container in containers_to_remove:
    print(f"Stopping and removing container: {container.name}")
    try:
        container.stop()
        container.remove()
        print(f"Successfully removed {container.name}")
    except Exception as e:
        print(f"Failed to remove {container.name}: {e}")

print("All specified containers have been removed.")
