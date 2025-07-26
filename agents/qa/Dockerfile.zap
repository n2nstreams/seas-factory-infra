# Dockerfile for OWASP ZAP Penetration Testing Agent
# Night 78: Final security scan & penetration test script (OWASP ZAP).

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99
ENV ZAP_HOME=/opt/zaproxy
ENV ZAP_VERSION=2.14.0
ENV JAVA_OPTS="-Xmx2g"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    openjdk-11-jdk \
    xvfb \
    firefox-esr \
    unzip \
    git \
    procps \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Download and install OWASP ZAP
RUN cd /opt && \
    wget -q "https://github.com/zaproxy/zaproxy/releases/download/v${ZAP_VERSION}/ZAP_${ZAP_VERSION}_Linux.tar.gz" -O zap.tar.gz && \
    tar -xzf zap.tar.gz && \
    mv "ZAP_${ZAP_VERSION}" zaproxy && \
    rm zap.tar.gz && \
    chmod +x /opt/zaproxy/zap.sh

# Create symlink for easier access
RUN ln -sf /opt/zaproxy/zap.sh /usr/local/bin/zap.sh

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install additional ZAP-specific dependencies
RUN pip install --no-cache-dir \
    python-zaproxy \
    beautifulsoup4 \
    lxml \
    selenium \
    webdriver-manager

# Copy source code
COPY . .

# Create ZAP configuration directory
RUN mkdir -p /app/zap-config /app/zap-sessions /app/zap-results

# Create ZAP configuration files
RUN echo "ZAP configuration directory created" > /app/zap-config/README.txt

# Create startup script
COPY <<'EOF' /app/start-zap-service.sh
#!/bin/bash

# Start virtual display
echo "Starting virtual display..."
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &

# Wait for display to be ready
sleep 2

# Start ZAP daemon if ZAP_DAEMON is set
if [ "$ZAP_DAEMON" = "true" ]; then
    echo "Starting ZAP daemon..."
    /opt/zaproxy/zap.sh \
        -daemon \
        -host 0.0.0.0 \
        -port 8090 \
        -config api.key=${ZAP_API_KEY:-changeme} \
        -config api.addrs.addr.name=.* \
        -config api.addrs.addr.regex=true \
        -config scanner.strength=MEDIUM \
        -config view.mode=attack \
        > /app/zap-results/zap-daemon.log 2>&1 &
    
    # Wait for ZAP to start
    echo "Waiting for ZAP daemon to start..."
    for i in {1..60}; do
        if curl -s "http://localhost:8090/JSON/core/view/version/?apikey=${ZAP_API_KEY:-changeme}" > /dev/null; then
            echo "ZAP daemon started successfully"
            break
        fi
        sleep 2
    done
fi

# Start the main application
echo "Starting ZAP Penetration Testing Service..."
exec python -m uvicorn zap_main:app --host 0.0.0.0 --port ${PORT:-8085}
EOF

RUN chmod +x /app/start-zap-service.sh

# Create health check script
COPY <<'EOF' /app/health-check.sh
#!/bin/bash

# Check if the FastAPI service is running
if ! curl -s http://localhost:${PORT:-8085}/health > /dev/null; then
    echo "FastAPI service is not responding"
    exit 1
fi

# Check if ZAP daemon is running (if enabled)
if [ "$ZAP_DAEMON" = "true" ]; then
    if ! curl -s "http://localhost:8090/JSON/core/view/version/?apikey=${ZAP_API_KEY:-changeme}" > /dev/null; then
        echo "ZAP daemon is not responding"
        exit 1
    fi
fi

echo "ZAP Penetration Testing Service is healthy"
exit 0
EOF

RUN chmod +x /app/health-check.sh

# Create ZAP session cleanup script
COPY <<'EOF' /app/cleanup-zap-sessions.sh
#!/bin/bash

echo "Cleaning up ZAP sessions..."

# Remove old session files (older than 24 hours)
find /app/zap-sessions -name "*.session" -mtime +1 -delete 2>/dev/null || true

# Remove old result files (older than 7 days)
find /app/zap-results -name "*.json" -mtime +7 -delete 2>/dev/null || true
find /app/zap-results -name "*.html" -mtime +7 -delete 2>/dev/null || true
find /app/zap-results -name "*.xml" -mtime +7 -delete 2>/dev/null || true

# Remove old log files (older than 7 days)
find /app/zap-results -name "*.log" -mtime +7 -delete 2>/dev/null || true

echo "ZAP session cleanup completed"
EOF

RUN chmod +x /app/cleanup-zap-sessions.sh

# Create user for running ZAP (security best practice)
RUN useradd -m -u 1001 -s /bin/bash zapuser && \
    chown -R zapuser:zapuser /app /opt/zaproxy

# Switch to non-root user
USER zapuser

# Expose ports
EXPOSE 8085 8090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /app/health-check.sh

# Default environment variables
ENV ZAP_API_KEY=changeme
ENV ZAP_DAEMON=false
ENV PORT=8085
ENV HOST=0.0.0.0

# Set the startup command
CMD ["/app/start-zap-service.sh"] 