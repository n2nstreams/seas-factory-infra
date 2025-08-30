#!/bin/bash

# Night 68: DevAgent K8s POC Cleanup Script
# Removes all Kubernetes resources for the DevAgent POC

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

echo -e "${BLUE}🧹 Night 68: DevAgent K8s POC Cleanup${NC}"
echo -e "${BLUE}======================================${NC}"
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

# Function to confirm deletion
confirm_deletion() {
    echo -e "${YELLOW}⚠ WARNING: This will delete all DevAgent K8s resources!${NC}"
    echo ""
    echo "Resources to be deleted:"
    echo "- Namespace: $NAMESPACE (and all resources within)"
    echo "- ClusterRole: devagent-cluster-role"
    echo "- ClusterRoleBinding: devagent-cluster-role-binding"
    echo ""
    
    if [[ "${FORCE_DELETE:-false}" != "true" ]]; then
        read -p "Are you sure you want to proceed? (type 'yes' to confirm): " -r
        if [[ $REPLY != "yes" ]]; then
            echo "Cleanup cancelled."
            exit 1
        fi
    fi
}

# Function to get cluster credentials
get_cluster_credentials() {
    print_info "Getting cluster credentials..."
    
    if ! gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION --project=$PROJECT_ID 2>/dev/null; then
        print_warning "Could not get cluster credentials. Cluster may not exist."
        print_info "If cluster was deleted, cleanup is complete."
        exit 0
    fi
    
    print_status "Cluster credentials configured"
}

# Function to delete namespace resources
delete_namespace_resources() {
    print_info "Deleting namespace resources..."
    
    if kubectl get namespace $NAMESPACE &>/dev/null; then
        # Delete specific resources first (to ensure proper cleanup)
        print_info "Deleting ingress resources..."
        kubectl delete ingress --all -n $NAMESPACE --ignore-not-found=true
        
        print_info "Deleting services..."
        kubectl delete services --all -n $NAMESPACE --ignore-not-found=true
        
        print_info "Deleting deployments..."
        kubectl delete deployments --all -n $NAMESPACE --ignore-not-found=true
        
        print_info "Deleting HPA and VPA..."
        kubectl delete hpa --all -n $NAMESPACE --ignore-not-found=true
        kubectl delete vpa --all -n $NAMESPACE --ignore-not-found=true
        
        print_info "Deleting secrets and configmaps..."
        kubectl delete secrets --all -n $NAMESPACE --ignore-not-found=true
        kubectl delete configmaps --all -n $NAMESPACE --ignore-not-found=true
        
        print_info "Deleting service accounts and RBAC..."
        kubectl delete serviceaccounts --all -n $NAMESPACE --ignore-not-found=true
        kubectl delete rolebindings --all -n $NAMESPACE --ignore-not-found=true
        kubectl delete roles --all -n $NAMESPACE --ignore-not-found=true
        
        # Delete the namespace itself
        print_info "Deleting namespace..."
        kubectl delete namespace $NAMESPACE --ignore-not-found=true
        
        # Wait for namespace deletion
        print_info "Waiting for namespace deletion..."
        while kubectl get namespace $NAMESPACE &>/dev/null; do
            echo -n "."
            sleep 2
        done
        echo ""
        
        print_status "Namespace and all resources deleted"
    else
        print_warning "Namespace $NAMESPACE does not exist"
    fi
}

# Function to delete cluster-wide resources
delete_cluster_resources() {
    print_info "Deleting cluster-wide resources..."
    
    # Delete ClusterRole
    kubectl delete clusterrole devagent-cluster-role --ignore-not-found=true
    
    # Delete ClusterRoleBinding
    kubectl delete clusterrolebinding devagent-cluster-role-binding --ignore-not-found=true
    
    print_status "Cluster-wide resources deleted"
}

# Function to cleanup Google Cloud resources
cleanup_gcp_resources() {
    print_info "Cleaning up Google Cloud resources..."
    
    # Delete Google Service Account (if created by this POC)
    GSA_NAME="devagent-k8s"
    GSA_EMAIL="$GSA_NAME@$PROJECT_ID.iam.gserviceaccount.com"
    
    if gcloud iam service-accounts describe $GSA_EMAIL --project=$PROJECT_ID &>/dev/null; then
        print_info "Deleting Google Service Account: $GSA_EMAIL"
        
        # Remove IAM policy bindings first
        gcloud projects remove-iam-policy-binding $PROJECT_ID \
            --member="serviceAccount:$GSA_EMAIL" \
            --role="roles/secretmanager.secretAccessor" \
            --quiet 2>/dev/null || true
        
        gcloud projects remove-iam-policy-binding $PROJECT_ID \
            --member="serviceAccount:$GSA_EMAIL" \
            --role="roles/cloudsql.client" \
            --quiet 2>/dev/null || true
        
        # Delete the service account
        gcloud iam service-accounts delete $GSA_EMAIL \
            --project=$PROJECT_ID \
            --quiet 2>/dev/null || true
        
        print_status "Google Service Account deleted"
    else
        print_info "Google Service Account does not exist or was not created by this POC"
    fi
}

# Function to cleanup load balancer resources
cleanup_load_balancer() {
    print_info "Cleaning up load balancer resources..."
    
    # Note: GKE automatically cleans up load balancers when services are deleted
    # But we can check for any remaining resources
    
    # List any remaining external IPs
    EXTERNAL_IPS=$(gcloud compute addresses list --filter="name~devagent" --format="value(name)" 2>/dev/null || echo "")
    
    if [[ -n "$EXTERNAL_IPS" ]]; then
        print_warning "Found external IP addresses that may need manual cleanup:"
        echo "$EXTERNAL_IPS"
        print_info "To delete: gcloud compute addresses delete <ADDRESS_NAME> --region=$REGION"
    fi
    
    print_status "Load balancer cleanup completed"
}

# Function to verify cleanup
verify_cleanup() {
    print_info "Verifying cleanup..."
    
    # Check namespace
    if kubectl get namespace $NAMESPACE &>/dev/null; then
        print_warning "Namespace $NAMESPACE still exists"
    else
        print_status "Namespace deleted"
    fi
    
    # Check cluster roles
    if kubectl get clusterrole devagent-cluster-role &>/dev/null; then
        print_warning "ClusterRole still exists"
    else
        print_status "ClusterRole deleted"
    fi
    
    # Check cluster role bindings
    if kubectl get clusterrolebinding devagent-cluster-role-binding &>/dev/null; then
        print_warning "ClusterRoleBinding still exists"
    else
        print_status "ClusterRoleBinding deleted"
    fi
    
    print_status "Cleanup verification completed"
}

# Function to show remaining resources
show_remaining_resources() {
    print_info "Checking for remaining DevAgent resources..."
    
    echo ""
    echo "Namespaces:"
    kubectl get namespaces | grep devagent || echo "None found"
    
    echo ""
    echo "ClusterRoles:"
    kubectl get clusterroles | grep devagent || echo "None found"
    
    echo ""
    echo "ClusterRoleBindings:"
    kubectl get clusterrolebindings | grep devagent || echo "None found"
    
    echo ""
    echo "Google Service Accounts:"
    gcloud iam service-accounts list --filter="email~devagent-k8s" --format="value(email)" 2>/dev/null || echo "None found"
}

# Main cleanup function
main() {
    print_info "Starting cleanup..."
    
    confirm_deletion
    get_cluster_credentials
    delete_namespace_resources
    delete_cluster_resources
    
    # Optional GCP resource cleanup
    if [[ "${CLEANUP_GCP:-false}" == "true" ]]; then
        cleanup_gcp_resources
        cleanup_load_balancer
    fi
    
    verify_cleanup
    
    echo ""
    print_status "Cleanup completed successfully!"
    
    # Show remaining resources
    show_remaining_resources
    
    echo ""
    print_info "If you also want to delete the GKE cluster:"
    echo "terraform destroy (in terraform/ directory)"
    echo ""
    print_info "Or using gcloud:"
    echo "gcloud container clusters delete $CLUSTER_NAME --region=$REGION --project=$PROJECT_ID"
}

# Handle script arguments
case "${1:-cleanup}" in
    "cleanup")
        main
        ;;
    "namespace-only")
        get_cluster_credentials
        delete_namespace_resources
        ;;
    "verify")
        get_cluster_credentials
        verify_cleanup
        ;;
    "show-resources")
        get_cluster_credentials
        show_remaining_resources
        ;;
    *)
        echo "Usage: $0 {cleanup|namespace-only|verify|show-resources}"
        echo ""
        echo "Commands:"
        echo "  cleanup         - Full cleanup of all resources (default)"
        echo "  namespace-only  - Delete only namespace resources"
        echo "  verify          - Verify cleanup was successful"
        echo "  show-resources  - Show remaining DevAgent resources"
        echo ""
        echo "Environment variables:"
        echo "  FORCE_DELETE=true     - Skip confirmation prompt"
        echo "  CLEANUP_GCP=true      - Also cleanup Google Cloud resources"
        exit 1
        ;;
esac 