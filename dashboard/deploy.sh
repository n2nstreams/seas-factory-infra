#!/bin/bash

# SaaS Factory Dashboard Deployment Script
# Supports: local, development, staging, production

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT="${1:-local}"
SERVICE_NAME="saas-factory-dashboard"
PORT="${PORT:-8000}"
DOCKER_IMAGE="gcr.io/saas-factory-dev/dashboard"

# Functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✓ $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠ $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ✗ $1${NC}"
}

usage() {
    echo "Usage: $0 [ENVIRONMENT]"
    echo ""
    echo "Environments:"
    echo "  local        - Local development deployment"
    echo "  development  - Development environment"
    echo "  staging      - Staging environment"
    echo "  production   - Production environment"
    echo ""
    echo "Examples:"
    echo "  $0 local"
    echo "  $0 production"
    echo ""
}

check_dependencies() {
    log "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        error "pip3 is required but not installed"
        exit 1
    fi
    
    # Check Docker for non-local environments
    if [[ "$ENVIRONMENT" != "local" ]]; then
        if ! command -v docker &> /dev/null; then
            error "Docker is required for $ENVIRONMENT environment"
            exit 1
        fi
    fi
    
    success "Dependencies check passed"
}

install_dependencies() {
    log "Installing Python dependencies..."
    
    cd "$SCRIPT_DIR"
    
    # Create virtual environment if it doesn't exist
    if [[ ! -d "venv" ]]; then
        log "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    pip install -r requirements.txt
    
    success "Dependencies installed"
}

build_docker_image() {
    log "Building Docker image..."
    
    cd "$SCRIPT_DIR"
    
    # Build image with version tag
    VERSION=$(date +%Y%m%d-%H%M%S)
    docker build -t "$DOCKER_IMAGE:$VERSION" .
    docker tag "$DOCKER_IMAGE:$VERSION" "$DOCKER_IMAGE:latest"
    
    success "Docker image built: $DOCKER_IMAGE:$VERSION"
}

deploy_local() {
    log "Deploying to local environment..."
    
    install_dependencies
    
    # Create .env file if it doesn't exist
    if [[ ! -f ".env" ]]; then
        log "Creating .env file..."
        cat > .env << EOF
# Local Development Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true
LOG_LEVEL=DEBUG
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
MAX_CONNECTIONS=50
MAX_HISTORY_SIZE=500
PING_INTERVAL=30
EOF
    fi
    
    # Start the service
    log "Starting dashboard service..."
    source venv/bin/activate
    
    if [[ "$2" == "background" ]]; then
        nohup python app.py > dashboard.log 2>&1 &
        echo $! > dashboard.pid
        log "Dashboard started in background (PID: $(cat dashboard.pid))"
        log "Logs: tail -f dashboard.log"
    else
        python app.py
    fi
}

deploy_development() {
    log "Deploying to development environment..."
    
    check_dependencies
    build_docker_image
    
    # Create docker-compose.yml for development
    cat > docker-compose.dev.yml << EOF
version: '3.8'
services:
  dashboard:
    image: $DOCKER_IMAGE:latest
    ports:
      - "8000:8000"
    environment:
      - HOST=0.0.0.0
      - PORT=8000
      - DEBUG=true
      - LOG_LEVEL=INFO
      - CORS_ORIGINS=["http://localhost:3000", "https://dev.forge95.com"]
      - MAX_CONNECTIONS=100
      - MAX_HISTORY_SIZE=1000
      - PING_INTERVAL=30
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
EOF
    
    # Deploy with docker-compose
    docker-compose -f docker-compose.dev.yml up -d
    
    success "Development deployment completed"
}

deploy_staging() {
    log "Deploying to staging environment..."
    
    check_dependencies
    build_docker_image
    
    # Push to registry
    docker push "$DOCKER_IMAGE:latest"
    
    # Deploy to staging (example for Google Cloud Run)
    if command -v gcloud &> /dev/null; then
        log "Deploying to Google Cloud Run (staging)..."
        gcloud run deploy dashboard-staging \
            --image "$DOCKER_IMAGE:latest" \
            --platform managed \
            --region us-central1 \
            --allow-unauthenticated \
            --set-env-vars "DEBUG=false,LOG_LEVEL=INFO,PORT=8080" \
            --memory 1Gi \
            --cpu 1 \
            --min-instances 0 \
            --max-instances 10
    else
        warning "gcloud CLI not found, skipping Cloud Run deployment"
    fi
    
    success "Staging deployment completed"
}

deploy_production() {
    log "Deploying to production environment..."
    
    # Confirmation prompt
    echo -e "${YELLOW}⚠️  You are about to deploy to PRODUCTION environment.${NC}"
    echo -e "${YELLOW}   This will affect live users and services.${NC}"
    echo ""
    read -p "Are you sure you want to continue? (yes/no): " -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]es$ ]]; then
        log "Deployment cancelled by user"
        exit 0
    fi
    
    check_dependencies
    build_docker_image
    
    # Push to registry
    docker push "$DOCKER_IMAGE:latest"
    
    # Deploy to production
    if command -v gcloud &> /dev/null; then
        log "Deploying to Google Cloud Run (production)..."
        gcloud run deploy dashboard \
            --image "$DOCKER_IMAGE:latest" \
            --platform managed \
            --region us-central1 \
            --allow-unauthenticated \
            --set-env-vars "DEBUG=false,LOG_LEVEL=WARNING,PORT=8080" \
            --memory 2Gi \
            --cpu 2 \
            --min-instances 1 \
            --max-instances 50 \
            --timeout 300
    else
        warning "gcloud CLI not found, skipping Cloud Run deployment"
    fi
    
    success "Production deployment completed"
}

health_check() {
    log "Performing health check..."
    
    local url="http://localhost:$PORT/health"
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -s -f "$url" > /dev/null; then
            success "Health check passed"
            return 0
        fi
        
        log "Health check attempt $attempt/$max_attempts failed, retrying in 2 seconds..."
        sleep 2
        ((attempt++))
    done
    
    error "Health check failed after $max_attempts attempts"
    return 1
}

generate_summary() {
    log "Generating deployment summary..."
    
    cat << EOF

╔══════════════════════════════════════════════════════════════════════════════╗
║                           DEPLOYMENT SUMMARY                                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Environment: $ENVIRONMENT                                                    ║
║ Service:     $SERVICE_NAME                                                   ║
║ Port:        $PORT                                                           ║
║ Time:        $(date)                                                         ║
║ Status:      SUCCESS                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

Service URLs:
• Health Check: http://localhost:$PORT/health
• API Docs:     http://localhost:$PORT/docs
• Dashboard:    http://localhost:$PORT/dashboard
• WebSocket:    ws://localhost:$PORT/ws/{client_id}

Monitoring:
• Logs:         tail -f dashboard.log
• Metrics:      curl http://localhost:$PORT/api/metrics
• WebSocket:    curl http://localhost:$PORT/api/websocket/stats

EOF
}

# Main deployment logic
main() {
    log "Starting deployment for environment: $ENVIRONMENT"
    
    case "$ENVIRONMENT" in
        "local")
            deploy_local "$@"
            ;;
        "development" | "dev")
            deploy_development
            ;;
        "staging")
            deploy_staging
            ;;
        "production" | "prod")
            deploy_production
            ;;
        "help" | "-h" | "--help")
            usage
            exit 0
            ;;
        *)
            error "Unknown environment: $ENVIRONMENT"
            usage
            exit 1
            ;;
    esac
    
    # Run health check (except for local background mode)
    if [[ "$ENVIRONMENT" == "local" && "$2" == "background" ]]; then
        log "Skipping health check for background mode"
        log "Run 'curl http://localhost:$PORT/health' to check service health"
    else
        sleep 5  # Give service time to start
        health_check
    fi
    
    generate_summary
    success "Deployment completed successfully!"
}

# Trap to handle cleanup
cleanup() {
    log "Cleaning up..."
    # Add any cleanup logic here
}

trap cleanup EXIT

# Run main function with all arguments
main "$@" 