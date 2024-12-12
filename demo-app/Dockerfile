# Use the official Python image from the Docker Hub
FROM python:3.11.9
ENV PYTHONUNBUFFERED True
# Set the working directory inside the container to match the root folder name
ENV APP_HOME /demo-app
WORKDIR $APP_HOME

#  Credentials
COPY dk_credentials.json $APP_HOME/dk_credentials.json
ENV GOOGLE_APPLICATION_CREDENTIALS=$APP_HOME/dk_credentials.json

# Copy the requirements file into the container
RUN pip install --upgrade pip
COPY requirements.txt  $APP_HOME/requirements.txt
RUN pip install --no-cache-dir -r  $APP_HOME/requirements.txt


# Copy the rest of the application code into the working directory
COPY .  $APP_HOME

ENV HOSTNAME "0.0.0.0"
# Expose the port the app runs on
EXPOSE 8080

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
