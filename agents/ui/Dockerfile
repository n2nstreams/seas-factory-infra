FROM node:18-slim as node-base

# Install html-to-react CLI globally
RUN npm install -g html-to-react

FROM python:3.11-slim

# Install Node.js and npm in Python container
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy html-to-react from node-base
COPY --from=node-base /usr/local/lib/node_modules /usr/local/lib/node_modules
COPY --from=node-base /usr/local/bin/html-to-react /usr/local/bin/

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 uidevagent && chown -R uidevagent:uidevagent /app
USER uidevagent

# Expose port
EXPOSE 8085

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8085/health || exit 1

# Run the application
CMD ["python", "main.py"] 