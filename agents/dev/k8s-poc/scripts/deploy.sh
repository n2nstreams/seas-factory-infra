#!/bin/bash

# Night 68: DevAgent K8s POC Deployment Script
# Deploys DevAgent to GKE Autopilot for portability demonstration

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
K8S_POC_DIR="$(dirname "$SCRIPT_DIR")"
MANIFESTS_DIR="$K8S_POC_DIR/manifests"

# Configuration
PROJECT_ID="${PROJECT_ID:-saas-factory-prod}"
CLUSTER_NAME="${CLUSTER_NAME:-devagent-poc-cluster}"
REGION="${REGION:-us-central1}"
NAMESPACE="devagent-poc"

echo -e "${BLUE}🚀 Night 68: DevAgent K8s POC Deployment${NC}"
echo -e "${BLUE}============================================${NC}"
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

# Function to check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check required tools
    for tool in gcloud kubectl; do
        if ! command -v $tool &> /dev/null; then
            print_error "$tool is not installed"
            exit 1
        fi
    done
    
    # Check gcloud authentication
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "Not authenticated with gcloud. Run: gcloud auth login"
        exit 1
    fi
    
    # Set project
    gcloud config set project $PROJECT_ID
    
    print_status "Prerequisites verified"
}

# Function to get cluster credentials
get_cluster_credentials() {
    print_info "Getting cluster credentials..."
    
    if ! gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION --project=$PROJECT_ID; then
        print_error "Failed to get cluster credentials. Make sure the cluster exists."
        print_info "To create cluster, run: terraform apply in terraform/ directory"
        exit 1
    fi
    
    print_status "Cluster credentials configured"
}

# Function to verify cluster is Autopilot
verify_autopilot_cluster() {
    print_info "Verifying GKE Autopilot cluster..."
    
    CLUSTER_MODE=$(gcloud container clusters describe $CLUSTER_NAME --region=$REGION --format="value(autopilot.enabled)")
    
    if [[ "$CLUSTER_MODE" != "True" ]]; then
        print_warning "Cluster is not in Autopilot mode. This POC is designed for GKE Autopilot."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        print_status "GKE Autopilot cluster verified"
    fi
}

# Function to create namespace
create_namespace() {
    print_info "Creating namespace..."
    
    kubectl apply -f "$MANIFESTS_DIR/namespace.yaml"
    
    # Wait for namespace to be ready
    kubectl wait --for=condition=Active namespace/$NAMESPACE --timeout=60s
    
    print_status "Namespace $NAMESPACE created"
}

# Function to sync secrets from Google Secret Manager
sync_secrets() {
    print_info "Syncing secrets from Google Secret Manager..."
    
    # Check if sync-secrets.sh exists and run it
    if [[ -f "$SCRIPT_DIR/sync-secrets.sh" ]]; then
        chmod +x "$SCRIPT_DIR/sync-secrets.sh"
        "$SCRIPT_DIR/sync-secrets.sh"
    else
        print_warning "sync-secrets.sh not found. Using template secrets."
        print_warning "Make sure to update secrets with actual values before production use."
        
        # Apply template secret (with placeholder values)
        kubectl apply -f "$MANIFESTS_DIR/secret.yaml"
    fi
    
    print_status "Secrets configured"
}

# Function to apply configuration
apply_configuration() {
    print_info "Applying configuration..."
    
    kubectl apply -f "$MANIFESTS_DIR/configmap.yaml"
    kubectl apply -f "$MANIFESTS_DIR/rbac.yaml"
    
    print_status "Configuration applied"
}

# Function to deploy DevAgent
deploy_devagent() {
    print_info "Deploying DevAgent..."
    
    # Update image name with actual project ID
    sed -i.bak "s/PROJECT_ID/$PROJECT_ID/g" "$MANIFESTS_DIR/deployment.yaml"
    
    kubectl apply -f "$MANIFESTS_DIR/deployment.yaml"
    kubectl apply -f "$MANIFESTS_DIR/service.yaml"
    kubectl apply -f "$MANIFESTS_DIR/hpa.yaml"
    
    # Restore original file
    mv "$MANIFESTS_DIR/deployment.yaml.bak" "$MANIFESTS_DIR/deployment.yaml"
    
    print_status "DevAgent deployment created"
}

# Function to apply ingress (optional)
apply_ingress() {
    print_info "Applying ingress configuration..."
    
    if [[ "${DEPLOY_INGRESS:-false}" == "true" ]]; then
        kubectl apply -f "$MANIFESTS_DIR/ingress.yaml"
        print_status "Ingress configured"
    else
        print_info "Skipping ingress deployment (set DEPLOY_INGRESS=true to enable)"
    fi
}

# Function to wait for deployment
wait_for_deployment() {
    print_info "Waiting for deployment to be ready..."
    
    # Wait for deployment to be available
    kubectl wait --for=condition=Available deployment/devagent -n $NAMESPACE --timeout=300s
    
    # Wait for pods to be ready
    kubectl wait --for=condition=Ready pods -l app.kubernetes.io/name=devagent -n $NAMESPACE --timeout=300s
    
    print_status "Deployment is ready"
}

# Function to show deployment status
show_status() {
    print_info "Deployment Status:"
    echo ""
    
    echo "Pods:"
    kubectl get pods -n $NAMESPACE -l app.kubernetes.io/name=devagent
    echo ""
    
    echo "Services:"
    kubectl get services -n $NAMESPACE
    echo ""
    
    echo "HPA:"
    kubectl get hpa -n $NAMESPACE
    echo ""
    
    echo "Ingress:"
    kubectl get ingress -n $NAMESPACE 2>/dev/null || echo "No ingress configured"
    echo ""
}

# Function to show access information
show_access_info() {
    print_info "Access Information:"
    echo ""
    
    # Get external IP if LoadBalancer service exists
    EXTERNAL_IP=$(kubectl get service devagent-external -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
    
    if [[ -n "$EXTERNAL_IP" ]]; then
        echo "External access: http://$EXTERNAL_IP"
        echo "Health check: http://$EXTERNAL_IP/health"
        echo "API endpoint: http://$EXTERNAL_IP/generate"
    else
        echo "No external access configured. Use port forwarding:"
        echo "kubectl port-forward -n $NAMESPACE service/devagent 8083:8083"
        echo "Then access: http://localhost:8083"
    fi
    
    echo ""
    echo "Logs: kubectl logs -f deployment/devagent -n $NAMESPACE"
    echo "Shell: kubectl exec -it deployment/devagent -n $NAMESPACE -- /bin/bash"
}

# Function to run health check
run_health_check() {
    print_info "Running health check..."
    
    # Port forward for health check
    kubectl port-forward -n $NAMESPACE service/devagent 8083:8083 &
    PF_PID=$!
    
    # Wait for port forward to be ready
    sleep 5
    
    # Check health endpoint
    if curl -s http://localhost:8083/health > /dev/null; then
        print_status "Health check passed"
    else
        print_error "Health check failed"
    fi
    
    # Clean up port forward
    kill $PF_PID 2>/dev/null || true
}

# Main deployment function
main() {
    echo -e "${BLUE}Starting deployment...${NC}"
    
    check_prerequisites
    get_cluster_credentials
    verify_autopilot_cluster
    create_namespace
    sync_secrets
    apply_configuration
    deploy_devagent
    apply_ingress
    wait_for_deployment
    
    echo ""
    print_status "Deployment completed successfully!"
    echo ""
    
    show_status
    show_access_info
    
    # Run health check
    if [[ "${RUN_HEALTH_CHECK:-true}" == "true" ]]; then
        echo ""
        run_health_check
    fi
    
    echo ""
    print_status "Night 68 DevAgent K8s POC deployment complete!"
    echo -e "${GREEN}🎉 DevAgent is now running on GKE Autopilot${NC}"
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "status")
        get_cluster_credentials
        show_status
        ;;
    "health")
        get_cluster_credentials
        run_health_check
        ;;
    "logs")
        get_cluster_credentials
        kubectl logs -f deployment/devagent -n $NAMESPACE
        ;;
    "shell")
        get_cluster_credentials
        kubectl exec -it deployment/devagent -n $NAMESPACE -- /bin/bash
        ;;
    *)
        echo "Usage: $0 {deploy|status|health|logs|shell}"
        echo ""
        echo "Commands:"
        echo "  deploy  - Deploy DevAgent to GKE Autopilot (default)"
        echo "  status  - Show deployment status"
        echo "  health  - Run health check"
        echo "  logs    - Show DevAgent logs"
        echo "  shell   - Open shell in DevAgent pod"
        exit 1
        ;;
esac 