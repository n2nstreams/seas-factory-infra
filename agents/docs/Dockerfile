FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared components
COPY agents/shared/ ./shared/

# Copy agent code
COPY agents/docs/ ./

# Create user for security
RUN useradd -m -u 1000 docagent && chown -R docagent:docagent /app
USER docagent

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8089/health || exit 1

EXPOSE 8089

CMD ["python", "main.py"] 