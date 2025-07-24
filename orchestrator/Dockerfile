FROM python:3.12-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

ARG REQ_FILE=requirements-orchestrator.txt
COPY ${REQ_FILE} ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY orchestrator/ .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port (default for Cloud Run)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "from project_orchestrator import ProjectOrchestrator; ProjectOrchestrator()" || exit 1

# Run the application
CMD ["python", "api_server.py"] 