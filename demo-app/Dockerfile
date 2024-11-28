# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory inside the container to match the root folder name
WORKDIR /demo-app

# Copy the requirements file into the container
COPY requirements.txt /demo-app/requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r /demo-app/requirements.txt

# Copy the rest of the application code into the working directory
COPY . /demo-app

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application
CMD ["python", "app.py"]
