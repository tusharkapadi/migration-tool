# Use a Python 3 base image
FROM python:3

# Set the working directory in the container
WORKDIR /app

# Copy the Python script and dependencies
COPY . .

# Install the required Python packages
RUN pip install --no-cache-dir requests

# Set the entrypoint of the container to the Python script
ENTRYPOINT ["python", "sysdig_migrate.py"]

# Set the default command to run the script with no arguments
CMD ["--help"]
