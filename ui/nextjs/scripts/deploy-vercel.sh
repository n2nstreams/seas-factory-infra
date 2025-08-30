#!/bin/bash

# Vercel Deployment Script for Module 10: Hosting & Canary Deployments
# This script handles deployment to Vercel with canary deployment support

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="saas-factory-nextjs"
VERCEL_ORG_ID="${VERCEL_ORG_ID:-}"
VERCEL_PROJECT_ID="${VERCEL_PROJECT_ID:-}"
VERCEL_TOKEN="${VERCEL_TOKEN:-}"
ENVIRONMENT="${ENVIRONMENT:-production}"
CANARY_ENABLED="${CANARY_ENABLED:-false}"
INITIAL_TRAFFIC="${INITIAL_TRAFFIC:-10}"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v vercel &> /dev/null; then
        log_error "Vercel CLI is not installed. Please install it first:"
        echo "npm i -g vercel"
        exit 1
    fi
    
    if [ -z "$VERCEL_TOKEN" ]; then
        log_error "VERCEL_TOKEN environment variable is not set"
        exit 1
    fi
    
    if [ -z "$VERCEL_ORG_ID" ]; then
        log_warning "VERCEL_ORG_ID not set, will use default organization"
    fi
    
    if [ -z "$VERCEL_PROJECT_ID" ]; then
        log_warning "VERCEL_PROJECT_ID not set, will create new project"
    fi
    
    log_success "Prerequisites check passed"
}

# Build the project
build_project() {
    log_info "Building Next.js project..."
    
    # Clean previous build
    rm -rf .next
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        log_info "Installing dependencies..."
        npm install
    fi
    
    # Build the project
    npm run build
    
    if [ $? -eq 0 ]; then
        log_success "Project built successfully"
    else
        log_error "Build failed"
        exit 1
    fi
}

# Deploy to Vercel
deploy_to_vercel() {
    log_info "Deploying to Vercel..."
    
    # Set Vercel environment variables
    export VERCEL_TOKEN="$VERCEL_TOKEN"
    
    if [ ! -z "$VERCEL_ORG_ID" ]; then
        export VERCEL_ORG_ID="$VERCEL_ORG_ID"
    fi
    
    if [ ! -z "$VERCEL_PROJECT_ID" ]; then
        export VERCEL_PROJECT_ID="$VERCEL_PROJECT_ID"
    fi
    
    # Deploy command
    if [ "$ENVIRONMENT" = "production" ]; then
        vercel --prod --yes
    else
        vercel --yes
    fi
    
    if [ $? -eq 0 ]; then
        log_success "Deployment completed successfully"
    else
        log_error "Deployment failed"
        exit 1
    fi
}

# Configure canary deployment
configure_canary() {
    if [ "$CANARY_ENABLED" = "true" ]; then
        log_info "Configuring canary deployment..."
        
        # Wait for deployment to be ready
        sleep 10
        
        # Start canary deployment with initial traffic
        log_info "Starting canary deployment with ${INITIAL_TRAFFIC}% traffic..."
        
        # Get the deployment URL
        DEPLOYMENT_URL=$(vercel ls --json | jq -r '.[0].url' 2>/dev/null || echo "")
        
        if [ ! -z "$DEPLOYMENT_URL" ]; then
            # Start canary deployment
            curl -X POST "${DEPLOYMENT_URL}/api/canary" \
                -H "Content-Type: application/json" \
                -d "{\"action\": \"start\", \"trafficPercentage\": ${INITIAL_TRAFFIC}}" \
                --max-time 30 || log_warning "Could not start canary deployment via API"
            
            log_success "Canary deployment configured with ${INITIAL_TRAFFIC}% traffic"
        else
            log_warning "Could not determine deployment URL for canary configuration"
        fi
    else
        log_info "Canary deployment disabled, skipping configuration"
    fi
}

# Run health checks
run_health_checks() {
    log_info "Running health checks..."
    
    # Wait for deployment to be ready
    sleep 15
    
    # Get the deployment URL
    DEPLOYMENT_URL=$(vercel ls --json | jq -r '.[0].url' 2>/dev/null || echo "")
    
    if [ ! -z "$DEPLOYMENT_URL" ]; then
        # Check basic health
        if curl -f "${DEPLOYMENT_URL}/api/health" --max-time 10 >/dev/null 2>&1; then
            log_success "Health check passed"
        else
            log_warning "Health check failed"
        fi
        
        # Check canary status if enabled
        if [ "$CANARY_ENABLED" = "true" ]; then
            if curl -f "${DEPLOYMENT_URL}/api/canary" --max-time 10 >/dev/null 2>&1; then
                log_success "Canary API health check passed"
            else
                log_warning "Canary API health check failed"
            fi
        fi
    else
        log_warning "Could not determine deployment URL for health checks"
    fi
}

# Main deployment flow
main() {
    log_info "Starting Vercel deployment for Module 10: Hosting & Canary Deployments"
    log_info "Environment: $ENVIRONMENT"
    log_info "Canary enabled: $CANARY_ENABLED"
    log_info "Initial traffic: ${INITIAL_TRAFFIC}%"
    
    check_prerequisites
    build_project
    deploy_to_vercel
    configure_canary
    run_health_checks
    
    log_success "Deployment completed successfully!"
    log_info "Next steps:"
    log_info "1. Configure your domain in Vercel dashboard"
    log_info "2. Set up DNS records"
    log_info "3. Monitor canary deployment metrics"
    log_info "4. Gradually increase traffic as needed"
}

# Handle script arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --canary-enabled)
            CANARY_ENABLED="$2"
            shift 2
            ;;
        --initial-traffic)
            INITIAL_TRAFFIC="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --environment ENV     Deployment environment (default: production)"
            echo "  --canary-enabled BOOL Enable canary deployment (default: false)"
            echo "  --initial-traffic NUM Initial canary traffic percentage (default: 10)"
            echo "  --help                Show this help message"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run main function
main "$@"
