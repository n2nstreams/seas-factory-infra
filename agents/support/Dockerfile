# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY ./agents/support/requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container at /app
COPY . /app

# Make port 8089 available to the world outside this container
EXPOSE 8089

# Define environment variables
ENV PYTHONPATH=/app
ENV APP_MODULE="agents.support.main:app"
ENV HOST="0.0.0.0"
ENV PORT="8089"

# Run the application
CMD ["uvicorn", "agents.support.main:app", "--host", "0.0.0.0", "--port", "8089"] 