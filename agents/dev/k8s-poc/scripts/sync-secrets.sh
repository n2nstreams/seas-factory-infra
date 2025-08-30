#!/bin/bash

# Night 68: Secret Synchronization Script
# Syncs secrets from Google Secret Manager to Kubernetes Secrets

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${PROJECT_ID:-saas-factory-prod}"
NAMESPACE="devagent-poc"

echo -e "${BLUE}🔐 Syncing secrets from Google Secret Manager${NC}"
echo "Project ID: $PROJECT_ID"
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

# Function to get secret from Secret Manager
get_secret() {
    local secret_name=$1
    local version=${2:-latest}
    
    if gcloud secrets versions access $version --secret="$secret_name" --project="$PROJECT_ID" 2>/dev/null; then
        return 0
    else
        print_warning "Secret $secret_name not found in Secret Manager"
        return 1
    fi
}

# Function to create Kubernetes secret
create_k8s_secret() {
    print_info "Creating Kubernetes secret..."
    
    # Get secrets from Secret Manager
    OPENAI_API_KEY=$(get_secret "openai-api-key" || echo "")
    DB_PASSWORD=$(get_secret "db-password" || echo "")
    DB_USER=$(get_secret "db-user" || echo "devagent_user")
    DB_HOST=$(get_secret "db-host" || echo "10.0.0.1")
    GITHUB_TOKEN=$(get_secret "github-token" || echo "")
    
    # Fallback values if secrets don't exist
    if [[ -z "$OPENAI_API_KEY" ]]; then
        print_warning "Using placeholder for OPENAI_API_KEY"
        OPENAI_API_KEY="sk-placeholder-openai-key"
    fi
    
    if [[ -z "$DB_PASSWORD" ]]; then
        print_warning "Using default for DB_PASSWORD"
        DB_PASSWORD="password123"
    fi
    
    if [[ -z "$GITHUB_TOKEN" ]]; then
        print_warning "Using placeholder for GITHUB_TOKEN"
        GITHUB_TOKEN="ghp_placeholder-github-token"
    fi
    
    # Create the secret
    kubectl create secret generic devagent-secrets \
        --namespace="$NAMESPACE" \
        --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
        --from-literal=DB_PASSWORD="$DB_PASSWORD" \
        --from-literal=DB_USER="$DB_USER" \
        --from-literal=DB_HOST="$DB_HOST" \
        --from-literal=GITHUB_TOKEN="$GITHUB_TOKEN" \
        --from-literal=JWT_SECRET_KEY="jwt-secret-key-for-devagent-poc" \
        --from-literal=WEBHOOK_SECRET="webhook-secret-for-devagent" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    print_status "Kubernetes secret created/updated"
}

# Function to create Artifact Registry secret
create_registry_secret() {
    print_info "Creating Artifact Registry secret..."
    
    # Check if we need to create registry secret
    if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        # Get current gcloud credentials
        GCLOUD_KEY=$(gcloud auth print-access-token)
        
        # Create Docker config
        DOCKER_CONFIG=$(cat <<EOF
{
  "auths": {
    "us-central1-docker.pkg.dev": {
      "username": "oauth2accesstoken",
      "password": "$GCLOUD_KEY",
      "auth": "$(echo -n "oauth2accesstoken:$GCLOUD_KEY" | base64 -w 0)"
    }
  }
}
EOF
)
        
        # Create secret
        kubectl create secret generic artifact-registry-secret \
            --namespace="$NAMESPACE" \
            --type=kubernetes.io/dockerconfigjson \
            --from-literal=.dockerconfigjson="$DOCKER_CONFIG" \
            --dry-run=client -o yaml | kubectl apply -f -
        
        print_status "Artifact Registry secret created"
    else
        print_warning "Not authenticated with gcloud, using placeholder registry secret"
        
        # Create placeholder secret
        kubectl create secret generic artifact-registry-secret \
            --namespace="$NAMESPACE" \
            --type=kubernetes.io/dockerconfigjson \
            --from-literal=.dockerconfigjson='{"auths":{}}' \
            --dry-run=client -o yaml | kubectl apply -f -
    fi
}

# Function to setup Workload Identity (if available)
setup_workload_identity() {
    print_info "Setting up Workload Identity..."
    
    # Check if Workload Identity is enabled
    CLUSTER_NAME="${CLUSTER_NAME:-devagent-poc-cluster}"
    REGION="${REGION:-us-central1}"
    
    WI_ENABLED=$(gcloud container clusters describe $CLUSTER_NAME --region=$REGION --format="value(workloadIdentityConfig.workloadPool)" 2>/dev/null || echo "")
    
    if [[ -n "$WI_ENABLED" ]]; then
        # Create Google Service Account if it doesn't exist
        GSA_NAME="devagent-k8s"
        GSA_EMAIL="$GSA_NAME@$PROJECT_ID.iam.gserviceaccount.com"
        
        if ! gcloud iam service-accounts describe $GSA_EMAIL --project=$PROJECT_ID &>/dev/null; then
            gcloud iam service-accounts create $GSA_NAME \
                --display-name="DevAgent K8s Service Account" \
                --description="Service account for DevAgent running on GKE" \
                --project=$PROJECT_ID
            
            print_status "Google Service Account created: $GSA_EMAIL"
        fi
        
        # Grant necessary IAM roles
        gcloud projects add-iam-policy-binding $PROJECT_ID \
            --member="serviceAccount:$GSA_EMAIL" \
            --role="roles/secretmanager.secretAccessor"
        
        gcloud projects add-iam-policy-binding $PROJECT_ID \
            --member="serviceAccount:$GSA_EMAIL" \
            --role="roles/cloudsql.client"
        
        # Bind Kubernetes Service Account to Google Service Account
        gcloud iam service-accounts add-iam-policy-binding $GSA_EMAIL \
            --role="roles/iam.workloadIdentityUser" \
            --member="serviceAccount:$PROJECT_ID.svc.id.goog[$NAMESPACE/devagent-service-account]" \
            --project=$PROJECT_ID
        
        # Annotate Kubernetes Service Account
        kubectl annotate serviceaccount devagent-service-account \
            --namespace=$NAMESPACE \
            iam.gke.io/gcp-service-account=$GSA_EMAIL \
            --overwrite
        
        print_status "Workload Identity configured"
    else
        print_warning "Workload Identity not enabled on cluster"
    fi
}

# Function to validate secrets
validate_secrets() {
    print_info "Validating secrets..."
    
    # Check if secret exists
    if kubectl get secret devagent-secrets -n $NAMESPACE &>/dev/null; then
        print_status "devagent-secrets exists"
        
        # List secret keys
        echo "Secret keys:"
        kubectl get secret devagent-secrets -n $NAMESPACE -o jsonpath='{.data}' | jq -r 'keys[]' 2>/dev/null || echo "  (unable to list keys)"
    else
        print_error "devagent-secrets not found"
        return 1
    fi
    
    if kubectl get secret artifact-registry-secret -n $NAMESPACE &>/dev/null; then
        print_status "artifact-registry-secret exists"
    else
        print_error "artifact-registry-secret not found"
        return 1
    fi
}

# Main function
main() {
    print_info "Starting secret synchronization..."
    
    # Check prerequisites
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl not found"
        exit 1
    fi
    
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud not found"
        exit 1
    fi
    
    # Set project
    gcloud config set project $PROJECT_ID
    
    # Create secrets
    create_k8s_secret
    create_registry_secret
    
    # Setup Workload Identity if available
    setup_workload_identity
    
    # Validate
    validate_secrets
    
    echo ""
    print_status "Secret synchronization completed!"
    
    # Show next steps
    echo ""
    print_info "Next steps:"
    echo "1. Verify secrets: kubectl get secrets -n $NAMESPACE"
    echo "2. Update secret values if needed:"
    echo "   kubectl patch secret devagent-secrets -n $NAMESPACE -p '{\"data\":{\"OPENAI_API_KEY\":\"<base64-encoded-value>\"}}'"
    echo "3. Deploy DevAgent: ./deploy.sh"
}

# Handle arguments
case "${1:-sync}" in
    "sync")
        main
        ;;
    "validate")
        validate_secrets
        ;;
    "workload-identity")
        setup_workload_identity
        ;;
    *)
        echo "Usage: $0 {sync|validate|workload-identity}"
        echo ""
        echo "Commands:"
        echo "  sync               - Sync all secrets (default)"
        echo "  validate           - Validate existing secrets"
        echo "  workload-identity  - Setup Workload Identity only"
        exit 1
        ;;
esac 