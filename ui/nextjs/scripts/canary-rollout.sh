#!/bin/bash

# Canary Rollout Strategy Script for Module 10
# Manages gradual traffic increase and monitoring during canary deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOYMENT_URL="${DEPLOYMENT_URL:-}"
PHASE_1_TRAFFIC="${PHASE_1_TRAFFIC:-10}"
PHASE_2_TRAFFIC="${PHASE_2_TRAFFIC:-25}"
PHASE_3_TRAFFIC="${PHASE_3_TRAFFIC:-50}"
PHASE_4_TRAFFIC="${PHASE_4_TRAFFIC:-75}"
FINAL_TRAFFIC="${FINAL_TRAFFIC:-100}"
PHASE_DURATION="${PHASE_DURATION:-1800}" # 30 minutes in seconds
HEALTH_CHECK_INTERVAL="${HEALTH_CHECK_INTERVAL:-60}" # 1 minute in seconds
ROLLBACK_THRESHOLD="${ROLLBACK_THRESHOLD:-0.05}" # 5% error rate

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

# Check if deployment URL is provided
check_deployment_url() {
    if [ -z "$DEPLOYMENT_URL" ]; then
        log_error "DEPLOYMENT_URL environment variable is not set"
        echo "Please set DEPLOYMENT_URL to your Vercel deployment URL"
        exit 1
    fi
    
    log_success "Using deployment URL: $DEPLOYMENT_URL"
}

# Check canary status
check_canary_status() {
    log_info "Checking current canary status..."
    
    local response
    response=$(curl -s "${DEPLOYMENT_URL}/api/canary" --max-time 10 2>/dev/null || echo "")
    
    if [ -z "$response" ]; then
        log_error "Could not connect to canary API"
        return 1
    fi
    
    local is_active
    is_active=$(echo "$response" | jq -r '.data.status.isActive' 2>/dev/null || echo "false")
    
    if [ "$is_active" = "true" ]; then
        local current_traffic
        current_traffic=$(echo "$response" | jq -r '.data.status.currentTrafficPercentage' 2>/dev/null || echo "0")
        log_info "Canary is active with ${current_traffic}% traffic"
        return 0
    else
        log_info "Canary is not active"
        return 1
    fi
}

# Start canary deployment
start_canary() {
    log_info "Starting canary deployment with ${PHASE_1_TRAFFIC}% traffic..."
    
    local response
    response=$(curl -s -X POST "${DEPLOYMENT_URL}/api/canary" \
        -H "Content-Type: application/json" \
        -d "{\"action\": \"start\", \"trafficPercentage\": ${PHASE_1_TRAFFIC}}" \
        --max-time 30 2>/dev/null || echo "")
    
    if [ ! -z "$response" ]; then
        local success
        success=$(echo "$response" | jq -r '.success' 2>/dev/null || echo "false")
        
        if [ "$success" = "true" ]; then
            log_success "Canary deployment started successfully"
            return 0
        else
            log_error "Failed to start canary deployment"
            return 1
        fi
    else
        log_error "Could not start canary deployment"
        return 1
    fi
}

# Increase traffic to specified percentage
increase_traffic() {
    local target_traffic=$1
    local increment=$2
    
    log_info "Increasing traffic to ${target_traffic}% (increment: ${increment}%)..."
    
    local response
    response=$(curl -s -X POST "${DEPLOYMENT_URL}/api/canary" \
        -H "Content-Type: application/json" \
        -d "{\"action\": \"increase\", \"trafficPercentage\": ${increment}}" \
        --max-time 30 2>/dev/null || echo "")
    
    if [ ! -z "$response" ]; then
        local success
        success=$(echo "$response" | jq -r '.success' 2>/dev/null || echo "false")
        
        if [ "$success" = "true" ]; then
            log_success "Traffic increased to ${target_traffic}%"
            return 0
        else
            log_error "Failed to increase traffic"
            return 1
        fi
    else
        log_error "Could not increase traffic"
        return 1
    fi
}

# Check health metrics
check_health_metrics() {
    local response
    response=$(curl -s "${DEPLOYMENT_URL}/api/canary/metrics" --max-time 10 2>/dev/null || echo "")
    
    if [ -z "$response" ]; then
        log_warning "Could not fetch health metrics"
        return 1
    fi
    
    local error_rate
    error_rate=$(echo "$response" | jq -r '.data.performance.errorRate' 2>/dev/null || echo "0")
    
    local response_time
    response_time=$(echo "$response" | jq -r '.data.performance.responseTime' 2>/dev/null || echo "0")
    
    local uptime
    uptime=$(echo "$response" | jq -r '.data.performance.uptime' 2>/dev/null || echo "1")
    
    log_info "Health metrics - Error Rate: ${error_rate}, Response Time: ${response_time}ms, Uptime: ${uptime}"
    
    # Check if rollback is needed
    if (( $(echo "$error_rate > $ROLLBACK_THRESHOLD" | bc -l) )); then
        log_error "Error rate ${error_rate} exceeds threshold ${ROLLBACK_THRESHOLD} - triggering rollback"
        trigger_rollback
        return 1
    fi
    
    if (( $(echo "$response_time > 5000" | bc -l) )); then
        log_warning "Response time ${response_time}ms exceeds 5 second threshold"
    fi
    
    if (( $(echo "$uptime < 0.95" | bc -l) )); then
        log_warning "Uptime ${uptime} is below 95% threshold"
    fi
    
    return 0
}

# Trigger rollback
trigger_rollback() {
    log_error "Triggering emergency rollback..."
    
    local response
    response=$(curl -s -X POST "${DEPLOYMENT_URL}/api/canary" \
        -H "Content-Type: application/json" \
        -d "{\"action\": \"rollback\"}" \
        --max-time 30 2>/dev/null || echo "")
    
    if [ ! -z "$response" ]; then
        local success
        success=$(echo "$response" | jq -r '.success' 2>/dev/null || echo "false")
        
        if [ "$success" = "true" ]; then
            log_success "Rollback triggered successfully"
        else
            log_error "Failed to trigger rollback"
        fi
    else
        log_error "Could not trigger rollback"
    fi
}

# Monitor phase
monitor_phase() {
    local phase_name=$1
    local phase_duration=$2
    
    log_info "Starting ${phase_name} monitoring (duration: ${phase_duration}s)..."
    
    local start_time=$(date +%s)
    local end_time=$((start_time + phase_duration))
    
    while [ $(date +%s) -lt $end_time ]; do
        if ! check_health_metrics; then
            log_error "Health check failed during ${phase_name} - stopping rollout"
            return 1
        fi
        
        local remaining=$((end_time - $(date +%s)))
        log_info "Phase ${phase_name} - ${remaining}s remaining"
        
        sleep $HEALTH_CHECK_INTERVAL
    done
    
    log_success "Phase ${phase_name} monitoring completed successfully"
    return 0
}

# Execute rollout phases
execute_rollout() {
    log_info "Starting canary rollout strategy..."
    
    # Phase 1: 10% traffic
    log_info "=== Phase 1: ${PHASE_1_TRAFFIC}% traffic ==="
    if ! start_canary; then
        log_error "Failed to start canary deployment"
        return 1
    fi
    
    if ! monitor_phase "Phase 1" $PHASE_DURATION; then
        return 1
    fi
    
    # Phase 2: 25% traffic
    log_info "=== Phase 2: ${PHASE_2_TRAFFIC}% traffic ==="
    local increment_2=$((PHASE_2_TRAFFIC - PHASE_1_TRAFFIC))
    if ! increase_traffic $PHASE_2_TRAFFIC $increment_2; then
        return 1
    fi
    
    if ! monitor_phase "Phase 2" $PHASE_DURATION; then
        return 1
    fi
    
    # Phase 3: 50% traffic
    log_info "=== Phase 3: ${PHASE_3_TRAFFIC}% traffic ==="
    local increment_3=$((PHASE_3_TRAFFIC - PHASE_2_TRAFFIC))
    if ! increase_traffic $PHASE_3_TRAFFIC $increment_3; then
        return 1
    fi
    
    if ! monitor_phase "Phase 3" $PHASE_DURATION; then
        return 1
    fi
    
    # Phase 4: 75% traffic
    log_info "=== Phase 4: ${PHASE_4_TRAFFIC}% traffic ==="
    local increment_4=$((PHASE_4_TRAFFIC - PHASE_3_TRAFFIC))
    if ! increase_traffic $PHASE_4_TRAFFIC $increment_4; then
        return 1
    fi
    
    if ! monitor_phase "Phase 4" $PHASE_DURATION; then
        return 1
    fi
    
    # Final Phase: 100% traffic
    log_info "=== Final Phase: ${FINAL_TRAFFIC}% traffic ==="
    local increment_final=$((FINAL_TRAFFIC - PHASE_4_TRAFFIC))
    if ! increase_traffic $FINAL_TRAFFIC $increment_final; then
        return 1
    fi
    
    if ! monitor_phase "Final Phase" $PHASE_DURATION; then
        return 1
    fi
    
    log_success "Canary rollout completed successfully! All traffic now routed to new system."
}

# Main function
main() {
    log_info "Starting Canary Rollout Strategy for Module 10"
    log_info "Deployment URL: $DEPLOYMENT_URL"
    log_info "Phase durations: ${PHASE_DURATION}s each"
    log_info "Health check interval: ${HEALTH_CHECK_INTERVAL}s"
    log_info "Rollback threshold: ${ROLLBACK_THRESHOLD}"
    
    check_deployment_url
    
    if check_canary_status; then
        log_warning "Canary is already active. Please check current status."
        return 0
    fi
    
    execute_rollout
}

# Handle script arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --deployment-url)
            DEPLOYMENT_URL="$2"
            shift 2
            ;;
        --phase-duration)
            PHASE_DURATION="$2"
            shift 2
            ;;
        --health-check-interval)
            HEALTH_CHECK_INTERVAL="$2"
            shift 2
            ;;
        --rollback-threshold)
            ROLLBACK_THRESHOLD="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --deployment-url URL    Vercel deployment URL"
            echo "  --phase-duration SEC    Duration of each phase in seconds (default: 1800)"
            echo "  --health-check-interval SEC Health check interval in seconds (default: 60)"
            echo "  --rollback-threshold NUM Rollback threshold for error rate (default: 0.05)"
            echo "  --help                  Show this help message"
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
