FROM python:3.12-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all API gateway files (including shared modules that are now local)
COPY *.py ./

# Set the correct port (8000 not 8080)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"] 