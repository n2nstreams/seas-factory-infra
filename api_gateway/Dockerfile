FROM python:3.12-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create the api_gateway directory structure
RUN mkdir -p api_gateway

# Copy all Python files to the api_gateway directory
COPY *.py api_gateway/

# Create __init__.py in api_gateway directory
RUN touch api_gateway/__init__.py

# Set Python path to /app so api_gateway can be imported
ENV PYTHONPATH=/app

# Run the application
CMD ["python", "-m", "uvicorn", "api_gateway.app:app", "--host", "0.0.0.0", "--port", "8000"]