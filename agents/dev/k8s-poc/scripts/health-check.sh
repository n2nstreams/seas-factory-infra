#!/bin/bash

# Night 68: DevAgent K8s POC Health Check Script
# Comprehensive health monitoring for DevAgent running on GKE Autopilot

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${PROJECT_ID:-saas-factory-prod}"
CLUSTER_NAME="${CLUSTER_NAME:-devagent-poc-cluster}"
REGION="${REGION:-us-central1}"
NAMESPACE="devagent-poc"
TIMEOUT="${TIMEOUT:-30}"

echo -e "${BLUE}🔍 Night 68: DevAgent K8s POC Health Check${NC}"
echo -e "${BLUE}===========================================${NC}"
echo "Project ID: $PROJECT_ID"
echo "Cluster: $CLUSTER_NAME"
echo "Region: $REGION"
echo "Namespace: $NAMESPACE"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    local missing_tools=()
    
    for tool in kubectl gcloud curl jq; do
        if ! command_exists "$tool"; then
            missing_tools+=("$tool")
        fi
    done
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        print_error "Missing required tools: ${missing_tools[*]}"
        print_info "Please install missing tools and try again"
        exit 1
    fi
    
    print_status "Prerequisites verified"
}

# Function to get cluster credentials
get_cluster_credentials() {
    print_info "Getting cluster credentials..."
    
    if ! gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION --project=$PROJECT_ID 2>/dev/null; then
        print_error "Failed to get cluster credentials"
        print_info "Make sure the cluster exists and you have access"
        exit 1
    fi
    
    print_status "Cluster credentials configured"
}

# Function to check cluster health
check_cluster_health() {
    print_info "Checking cluster health..."
    
    # Check cluster status
    local cluster_status=$(gcloud container clusters describe $CLUSTER_NAME --region=$REGION --format="value(status)" 2>/dev/null)
    
    if [[ "$cluster_status" == "RUNNING" ]]; then
        print_status "Cluster is running"
    else
        print_error "Cluster status: $cluster_status"
        return 1
    fi
    
    # Check nodes
    local ready_nodes=$(kubectl get nodes --no-headers 2>/dev/null | awk '$2=="Ready" {count++} END {print count+0}')
    local total_nodes=$(kubectl get nodes --no-headers 2>/dev/null | wc -l)
    
    if [[ $ready_nodes -gt 0 ]]; then
        print_status "Nodes ready: $ready_nodes/$total_nodes"
    else
        print_error "No ready nodes found"
        return 1
    fi
}

# Function to check namespace
check_namespace() {
    print_info "Checking namespace..."
    
    if kubectl get namespace $NAMESPACE &>/dev/null; then
        local ns_status=$(kubectl get namespace $NAMESPACE -o jsonpath='{.status.phase}' 2>/dev/null)
        if [[ "$ns_status" == "Active" ]]; then
            print_status "Namespace $NAMESPACE is active"
        else
            print_warning "Namespace status: $ns_status"
        fi
    else
        print_error "Namespace $NAMESPACE not found"
        return 1
    fi
}

# Function to check deployment
check_deployment() {
    print_info "Checking DevAgent deployment..."
    
    if ! kubectl get deployment devagent -n $NAMESPACE &>/dev/null; then
        print_error "DevAgent deployment not found"
        return 1
    fi
    
    local desired=$(kubectl get deployment devagent -n $NAMESPACE -o jsonpath='{.spec.replicas}')
    local ready=$(kubectl get deployment devagent -n $NAMESPACE -o jsonpath='{.status.readyReplicas}')
    local available=$(kubectl get deployment devagent -n $NAMESPACE -o jsonpath='{.status.availableReplicas}')
    
    ready=${ready:-0}
    available=${available:-0}
    
    if [[ $ready -eq $desired ]] && [[ $available -eq $desired ]]; then
        print_status "Deployment ready: $ready/$desired replicas"
    else
        print_warning "Deployment not fully ready: $ready/$desired ready, $available/$desired available"
        
        # Show deployment status
        echo "Deployment conditions:"
        kubectl get deployment devagent -n $NAMESPACE -o jsonpath='{.status.conditions[*].type}: {.status.conditions[*].status}' 2>/dev/null || echo "Unable to get conditions"
        return 1
    fi
}

# Function to check pods
check_pods() {
    print_info "Checking DevAgent pods..."
    
    local pods=$(kubectl get pods -n $NAMESPACE -l app.kubernetes.io/name=devagent --no-headers 2>/dev/null)
    
    if [[ -z "$pods" ]]; then
        print_error "No DevAgent pods found"
        return 1
    fi
    
    local running_count=0
    local total_count=0
    
    while IFS= read -r line; do
        ((total_count++))
        local status=$(echo "$line" | awk '{print $3}')
        local ready=$(echo "$line" | awk '{print $2}')
        
        if [[ "$status" == "Running" ]] && [[ "$ready" =~ ^[0-9]+/[0-9]+$ ]]; then
            local ready_containers=$(echo "$ready" | cut -d'/' -f1)
            local total_containers=$(echo "$ready" | cut -d'/' -f2)
            
            if [[ $ready_containers -eq $total_containers ]]; then
                ((running_count++))
            fi
        fi
    done <<< "$pods"
    
    if [[ $running_count -eq $total_count ]] && [[ $total_count -gt 0 ]]; then
        print_status "Pods running: $running_count/$total_count"
    else
        print_warning "Pods status: $running_count/$total_count running"
        
        # Show pod details
        echo "Pod details:"
        kubectl get pods -n $NAMESPACE -l app.kubernetes.io/name=devagent -o wide 2>/dev/null || echo "Unable to get pod details"
        return 1
    fi
}

# Function to check services
check_services() {
    print_info "Checking services..."
    
    local services=("devagent" "devagent-external")
    local all_good=true
    
    for service in "${services[@]}"; do
        if kubectl get service $service -n $NAMESPACE &>/dev/null; then
            local type=$(kubectl get service $service -n $NAMESPACE -o jsonpath='{.spec.type}')
            local cluster_ip=$(kubectl get service $service -n $NAMESPACE -o jsonpath='{.spec.clusterIP}')
            
            if [[ "$type" == "LoadBalancer" ]]; then
                local external_ip=$(kubectl get service $service -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
                if [[ -n "$external_ip" ]]; then
                    print_status "Service $service ($type): $external_ip"
                else
                    print_warning "Service $service ($type): external IP pending"
                fi
            else
                print_status "Service $service ($type): $cluster_ip"
            fi
        else
            if [[ "$service" == "devagent" ]]; then
                print_error "Required service $service not found"
                all_good=false
            else
                print_info "Optional service $service not found"
            fi
        fi
    done
    
    if [[ "$all_good" != "true" ]]; then
        return 1
    fi
}

# Function to check secrets
check_secrets() {
    print_info "Checking secrets..."
    
    local secrets=("devagent-secrets" "artifact-registry-secret")
    
    for secret in "${secrets[@]}"; do
        if kubectl get secret $secret -n $NAMESPACE &>/dev/null; then
            local type=$(kubectl get secret $secret -n $NAMESPACE -o jsonpath='{.type}')
            print_status "Secret $secret ($type) exists"
        else
            print_error "Secret $secret not found"
            return 1
        fi
    done
}

# Function to check configmaps
check_configmaps() {
    print_info "Checking configmaps..."
    
    local configmaps=("devagent-config" "devagent-templates")
    
    for cm in "${configmaps[@]}"; do
        if kubectl get configmap $cm -n $NAMESPACE &>/dev/null; then
            print_status "ConfigMap $cm exists"
        else
            if [[ "$cm" == "devagent-config" ]]; then
                print_error "Required ConfigMap $cm not found"
                return 1
            else
                print_warning "Optional ConfigMap $cm not found"
            fi
        fi
    done
}

# Function to check HPA
check_hpa() {
    print_info "Checking Horizontal Pod Autoscaler..."
    
    if kubectl get hpa devagent-hpa -n $NAMESPACE &>/dev/null; then
        local current_replicas=$(kubectl get hpa devagent-hpa -n $NAMESPACE -o jsonpath='{.status.currentReplicas}')
        local desired_replicas=$(kubectl get hpa devagent-hpa -n $NAMESPACE -o jsonpath='{.status.desiredReplicas}')
        local min_replicas=$(kubectl get hpa devagent-hpa -n $NAMESPACE -o jsonpath='{.spec.minReplicas}')
        local max_replicas=$(kubectl get hpa devagent-hpa -n $NAMESPACE -o jsonpath='{.spec.maxReplicas}')
        
        print_status "HPA active: $current_replicas/$desired_replicas replicas (min: $min_replicas, max: $max_replicas)"
    else
        print_warning "HPA not found"
    fi
}

# Function to test HTTP endpoints
test_http_endpoints() {
    print_info "Testing HTTP endpoints..."
    
    # Get service endpoint
    local service_ip=""
    local service_port="8083"
    
    # Try external service first
    service_ip=$(kubectl get service devagent-external -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
    
    if [[ -z "$service_ip" ]]; then
        # Use port forwarding
        print_info "Using port forwarding for endpoint testing..."
        kubectl port-forward -n $NAMESPACE service/devagent 8083:8083 &
        local pf_pid=$!
        service_ip="localhost"
        
        # Wait for port forward to be ready
        sleep 3
    fi
    
    # Test health endpoint
    local health_url="http://$service_ip:$service_port/health"
    if curl -s --max-time $TIMEOUT "$health_url" > /dev/null; then
        print_status "Health endpoint responding: $health_url"
    else
        print_error "Health endpoint not responding: $health_url"
        if [[ -n "${pf_pid:-}" ]]; then
            kill $pf_pid 2>/dev/null || true
        fi
        return 1
    fi
    
    # Test readiness endpoint
    local ready_url="http://$service_ip:$service_port/ready"
    if curl -s --max-time $TIMEOUT "$ready_url" > /dev/null; then
        print_status "Readiness endpoint responding: $ready_url"
    else
        print_warning "Readiness endpoint not responding: $ready_url"
    fi
    
    # Test API docs endpoint
    local docs_url="http://$service_ip:$service_port/docs"
    if curl -s --max-time $TIMEOUT "$docs_url" > /dev/null; then
        print_status "API docs endpoint responding: $docs_url"
    else
        print_warning "API docs endpoint not responding: $docs_url"
    fi
    
    # Clean up port forward
    if [[ -n "${pf_pid:-}" ]]; then
        kill $pf_pid 2>/dev/null || true
    fi
}

# Function to check resource usage
check_resource_usage() {
    print_info "Checking resource usage..."
    
    # Get pod metrics (if metrics server is available)
    if kubectl top pods -n $NAMESPACE &>/dev/null; then
        echo "Pod resource usage:"
        kubectl top pods -n $NAMESPACE -l app.kubernetes.io/name=devagent
    else
        print_warning "Metrics server not available, skipping resource usage check"
    fi
    
    # Check resource quotas
    if kubectl get resourcequota -n $NAMESPACE &>/dev/null; then
        echo ""
        echo "Resource quotas:"
        kubectl get resourcequota -n $NAMESPACE
    fi
}

# Function to check logs for errors
check_logs() {
    print_info "Checking logs for errors..."
    
    local pods=$(kubectl get pods -n $NAMESPACE -l app.kubernetes.io/name=devagent -o name 2>/dev/null)
    
    if [[ -z "$pods" ]]; then
        print_warning "No pods found for log checking"
        return
    fi
    
    local error_count=0
    
    for pod in $pods; do
        local pod_name=$(basename "$pod")
        
        # Check for errors in logs (last 50 lines)
        local errors=$(kubectl logs $pod -n $NAMESPACE --tail=50 2>/dev/null | grep -i error | wc -l)
        
        if [[ $errors -gt 0 ]]; then
            ((error_count += errors))
            print_warning "Found $errors error(s) in $pod_name logs"
        fi
    done
    
    if [[ $error_count -eq 0 ]]; then
        print_status "No errors found in recent logs"
    else
        print_warning "Total errors found: $error_count"
        print_info "Use 'kubectl logs' to investigate further"
    fi
}

# Function to run comprehensive health check
run_comprehensive_check() {
    local checks=(
        "check_cluster_health"
        "check_namespace"
        "check_deployment"
        "check_pods"
        "check_services"
        "check_secrets"
        "check_configmaps"
        "check_hpa"
    )
    
    local failed_checks=()
    
    for check in "${checks[@]}"; do
        if ! $check; then
            failed_checks+=("$check")
        fi
        echo ""
    done
    
    # Optional checks (don't fail overall health)
    test_http_endpoints || true
    echo ""
    check_resource_usage || true
    echo ""
    check_logs || true
    
    echo ""
    if [[ ${#failed_checks[@]} -eq 0 ]]; then
        print_status "All critical health checks passed!"
        echo -e "${GREEN}🎉 DevAgent K8s deployment is healthy${NC}"
        return 0
    else
        print_error "Failed health checks: ${failed_checks[*]}"
        echo -e "${RED}❌ DevAgent K8s deployment has issues${NC}"
        return 1
    fi
}

# Function to show summary
show_summary() {
    print_info "Health Check Summary:"
    echo ""
    
    echo "Cluster: $CLUSTER_NAME ($REGION)"
    echo "Namespace: $NAMESPACE"
    echo "Time: $(date)"
    echo ""
    
    # Quick status overview
    local deployment_status=$(kubectl get deployment devagent -n $NAMESPACE -o jsonpath='{.status.conditions[?(@.type=="Available")].status}' 2>/dev/null || echo "Unknown")
    local pod_count=$(kubectl get pods -n $NAMESPACE -l app.kubernetes.io/name=devagent --no-headers 2>/dev/null | wc -l)
    local service_count=$(kubectl get services -n $NAMESPACE --no-headers 2>/dev/null | wc -l)
    
    echo "Deployment Available: $deployment_status"
    echo "Pods: $pod_count"
    echo "Services: $service_count"
}

# Main function
main() {
    check_prerequisites
    get_cluster_credentials
    
    case "${1:-all}" in
        "all")
            run_comprehensive_check
            ;;
        "quick")
            check_cluster_health && check_deployment && check_pods
            ;;
        "endpoints")
            test_http_endpoints
            ;;
        "logs")
            check_logs
            ;;
        "resources")
            check_resource_usage
            ;;
        "summary")
            show_summary
            ;;
        *)
            echo "Usage: $0 {all|quick|endpoints|logs|resources|summary}"
            echo ""
            echo "Commands:"
            echo "  all       - Run comprehensive health check (default)"
            echo "  quick     - Run quick health check (cluster, deployment, pods)"
            echo "  endpoints - Test HTTP endpoints only"
            echo "  logs      - Check logs for errors"
            echo "  resources - Check resource usage"
            echo "  summary   - Show deployment summary"
            exit 1
            ;;
    esac
}

# Run main function
main "$@" 