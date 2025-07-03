#!/bin/bash

# Night 7 - DevOps & AIOps Foundations Deployment Script
# This script automates the deployment of the SaaS Factory infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="summer-nexus-463503-e1"
REGION="us-central1"
IMAGE_TAG="0.1"

echo -e "${GREEN}🚀 Starting Night 7 Deployment - DevOps & AIOps Foundations${NC}"

# Check if required tools are installed
check_tools() {
    echo -e "${YELLOW}📋 Checking required tools...${NC}"
    
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}❌ gcloud CLI not found. Please install Google Cloud SDK.${NC}"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker not found. Please install Docker.${NC}"
        exit 1
    fi
    
    if ! command -v terraform &> /dev/null; then
        echo -e "${RED}❌ Terraform not found. Please install Terraform.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ All required tools are installed${NC}"
}

# Enable required APIs
enable_apis() {
    echo -e "${YELLOW}🔧 Enabling required Google Cloud APIs...${NC}"
    
    gcloud services enable \
        run.googleapis.com \
        compute.googleapis.com \
        clouddeploy.googleapis.com \
        monitoring.googleapis.com \
        billingbudgets.googleapis.com \
        pubsub.googleapis.com \
        artifactregistry.googleapis.com \
        vpcaccess.googleapis.com \
        sqladmin.googleapis.com \
        servicenetworking.googleapis.com \
        --project=$PROJECT_ID
    
    echo -e "${GREEN}✅ APIs enabled successfully${NC}"
}

# Build and push container image
build_and_push_image() {
    echo -e "${YELLOW}🏗️  Building and pushing container image...${NC}"
    
    # Navigate to the starter API directory
    cd ../../agents/dev/starter-api
    
    # Build the Docker image
    docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/saas-factory/api:$IMAGE_TAG .
    
    # Configure Docker to use gcloud as a credential helper
    gcloud auth configure-docker $REGION-docker.pkg.dev --quiet
    
    # Push the image
    docker push $REGION-docker.pkg.dev/$PROJECT_ID/saas-factory/api:$IMAGE_TAG
    
    # Go back to the infra directory
    cd ../../../infra/prod
    
    echo -e "${GREEN}✅ Container image built and pushed successfully${NC}"
}

# Deploy infrastructure
deploy_infrastructure() {
    echo -e "${YELLOW}🏗️  Deploying infrastructure with Terraform...${NC}"
    
    # Initialize Terraform
    terraform init
    
    # Plan the deployment
    terraform plan -out=night7.plan
    
    # Apply the plan
    terraform apply night7.plan
    
    echo -e "${GREEN}✅ Infrastructure deployed successfully${NC}"
}

# Verify deployment
verify_deployment() {
    echo -e "${YELLOW}🔍 Verifying deployment...${NC}"
    
    # Get the load balancer IP
    LB_IP=$(terraform output -raw lb_ip_address)
    
    # Wait for the load balancer to be ready
    echo "Waiting for load balancer to be ready..."
    sleep 60
    
    # Test the health endpoint
    echo "Testing health endpoint..."
    if curl -f -s "http://$LB_IP/health" > /dev/null; then
        echo -e "${GREEN}✅ Health endpoint is responding${NC}"
    else
        echo -e "${YELLOW}⚠️  Health endpoint not ready yet (this is normal for initial deployment)${NC}"
    fi
    
    # Display deployment information
    echo -e "\n${GREEN}📊 Deployment Summary:${NC}"
    echo "Project ID: $PROJECT_ID"
    echo "Region: $REGION"
    echo "Load Balancer IP: $LB_IP"
    echo "API Central URL: $(terraform output -raw api_central_url)"
    echo "API East URL: $(terraform output -raw api_east_url)"
    echo "Monitoring Dashboard: $(terraform output -raw monitoring_dashboard_url)"
    echo "Artifact Registry: $(terraform output -raw artifact_registry_repository)"
}

# Main deployment function
main() {
    echo -e "${GREEN}Starting deployment process...${NC}"
    
    check_tools
    enable_apis
    build_and_push_image
    deploy_infrastructure
    verify_deployment
    
    echo -e "\n${GREEN}🎉 Night 7 deployment completed successfully!${NC}"
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Update your DNS to point api.$PROJECT_ID.com to the load balancer IP"
    echo "2. Configure your Slack webhook token in terraform.tfvars"
    echo "3. Set up your billing account ID in terraform.tfvars"
    echo "4. Run 'terraform apply' again to enable monitoring and cost guards"
    echo "5. Test the DevOps and AIOps agents with: python agents/ops/devops_agent.py"
}

# Handle script arguments
case "${1:-}" in
    "apis")
        enable_apis
        ;;
    "build")
        build_and_push_image
        ;;
    "deploy")
        deploy_infrastructure
        ;;
    "verify")
        verify_deployment
        ;;
    "")
        main
        ;;
    *)
        echo -e "${RED}Usage: $0 [apis|build|deploy|verify]${NC}"
        echo "  apis    - Enable required APIs only"
        echo "  build   - Build and push container image only"
        echo "  deploy  - Deploy infrastructure only"
        echo "  verify  - Verify deployment only"
        echo "  (no args) - Run full deployment"
        exit 1
        ;;
esac 