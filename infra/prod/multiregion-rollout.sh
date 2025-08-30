#!/bin/bash

# Night 48 - Multi-region Blue-Green Rollout Script
# Deploys services to us-central1 and us-east1 with blue-green deployment strategy

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="summer-nexus-463503-e1"
PRIMARY_REGION="us-central1"
SECONDARY_REGION="us-east1"
IMAGE_TAG=${IMAGE_TAG:-$(date +%Y%m%d-%H%M%S)}
SERVICE_NAME="api-backend"
HEALTH_CHECK_TIMEOUT=300
ROLLBACK_THRESHOLD=5  # Number of failed health checks before rollback

# Traffic split stages for blue-green deployment
TRAFFIC_STAGES=(10 25 50 100)
STAGE_DURATION=120  # seconds between traffic increases

echo -e "${GREEN}🚀 Starting Night 48 - Multi-Region Blue-Green Deployment${NC}"
echo -e "${BLUE}Image Tag: ${IMAGE_TAG}${NC}"
echo -e "${BLUE}Primary Region: ${PRIMARY_REGION}${NC}"
echo -e "${BLUE}Secondary Region: ${SECONDARY_REGION}${NC}"

# Check if required tools are installed
check_tools() {
    echo -e "${YELLOW}📋 Checking required tools...${NC}"
    
    local tools=("gcloud" "docker" "terraform" "jq" "curl")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            echo -e "${RED}❌ $tool not found. Please install $tool.${NC}"
            exit 1
        fi
    done
    
    echo -e "${GREEN}✅ All required tools are installed${NC}"
}

# Validate current infrastructure
validate_infrastructure() {
    echo -e "${YELLOW}🔍 Validating current infrastructure...${NC}"
    
    # Check if services exist
    if ! gcloud run services describe "$SERVICE_NAME" --region="$PRIMARY_REGION" --project="$PROJECT_ID" &>/dev/null; then
        echo -e "${RED}❌ Service $SERVICE_NAME not found in $PRIMARY_REGION${NC}"
        exit 1
    fi
    
    if ! gcloud run services describe "${SERVICE_NAME}-east" --region="$SECONDARY_REGION" --project="$PROJECT_ID" &>/dev/null; then
        echo -e "${RED}❌ Service ${SERVICE_NAME}-east not found in $SECONDARY_REGION${NC}"
        exit 1
    fi
    
    # Check load balancer
    if ! gcloud compute global-addresses describe lb-ip --project="$PROJECT_ID" &>/dev/null; then
        echo -e "${RED}❌ Load balancer IP not found${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Infrastructure validation passed${NC}"
}

# Build and push container image to both regions
build_and_push_image() {
    echo -e "${YELLOW}🏗️  Building and pushing container image...${NC}"
    
    # Navigate to the starter API directory
    cd ../../agents/dev/starter-api
    
    # Build the Docker image
    local image_name="$PRIMARY_REGION-docker.pkg.dev/$PROJECT_ID/saas-factory/api:$IMAGE_TAG"
    docker build -t "$image_name" .
    
    # Configure Docker authentication
    gcloud auth configure-docker "$PRIMARY_REGION-docker.pkg.dev" --quiet
    
    # Push the image
    docker push "$image_name"
    
    # Tag and push to secondary region registry if different
    if [ "$SECONDARY_REGION" != "$PRIMARY_REGION" ]; then
        local secondary_image="$SECONDARY_REGION-docker.pkg.dev/$PROJECT_ID/saas-factory/api:$IMAGE_TAG"
        gcloud auth configure-docker "$SECONDARY_REGION-docker.pkg.dev" --quiet
        docker tag "$image_name" "$secondary_image"
        docker push "$secondary_image"
    fi
    
    # Go back to infra directory
    cd ../../../infra/prod
    
    echo -e "${GREEN}✅ Container image built and pushed successfully${NC}"
}

# Deploy new revision to a region without traffic
deploy_green_revision() {
    local region=$1
    local service_name=$2
    local revision_suffix=$3
    
    echo -e "${YELLOW}🔄 Deploying green revision to $region...${NC}"
    
    local image_url="$region-docker.pkg.dev/$PROJECT_ID/saas-factory/api:$IMAGE_TAG"
    local revision_name="${service_name}-${revision_suffix}-${IMAGE_TAG}"
    
    # Deploy new revision with 0% traffic
    gcloud run deploy "$service_name" \
        --image="$image_url" \
        --region="$region" \
        --project="$PROJECT_ID" \
        --revision-suffix="$revision_suffix-$IMAGE_TAG" \
        --no-traffic \
        --tag="green" \
        --service-account="run-sa@$PROJECT_ID.iam.gserviceaccount.com" \
        --vpc-connector="vpc-connector" \
        --vpc-egress="private-ranges-only" \
        --cpu="2" \
        --memory="2Gi" \
        --min-instances=0 \
        --max-instances=10 \
        --set-env-vars="DB_HOST=$(terraform output -raw cloudsql_postgres_instance_connection_name | cut -d: -f3),DB_NAME=factorydb,DB_PORT=5432,ENVIRONMENT=production,REGION=$region" \
        --quiet
    
    echo -e "${GREEN}✅ Green revision deployed to $region${NC}"
    return 0
}

# Perform health check on a specific revision
health_check() {
    local service_url=$1
    local check_name=$2
    
    echo -e "${CYAN}🏥 Performing health check: $check_name${NC}"
    
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s --max-time 10 "$service_url/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Health check passed ($attempt/$max_attempts)${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  Health check failed ($attempt/$max_attempts), retrying in 10s...${NC}"
            sleep 10
            ((attempt++))
        fi
    done
    
    echo -e "${RED}❌ Health check failed after $max_attempts attempts${NC}"
    return 1
}

# Get the URL for a specific revision tag
get_revision_url() {
    local service_name=$1
    local region=$2
    local tag=$3
    
    gcloud run services describe "$service_name" \
        --region="$region" \
        --project="$PROJECT_ID" \
        --format="value(status.traffic[?tag=='$tag'].url)" \
        2>/dev/null | head -n1
}

# Split traffic progressively for blue-green deployment
progressive_traffic_split() {
    local service_name=$1
    local region=$2
    local green_revision=$3
    
    echo -e "${PURPLE}🔀 Starting progressive traffic split for $service_name in $region${NC}"
    
    for stage in "${TRAFFIC_STAGES[@]}"; do
        echo -e "${YELLOW}📊 Shifting ${stage}% traffic to green revision...${NC}"
        
        # Calculate blue traffic percentage
        local blue_traffic=$((100 - stage))
        
        # Update traffic allocation
        gcloud run services update-traffic "$service_name" \
            --region="$region" \
            --project="$PROJECT_ID" \
            --to-revisions="$green_revision=$stage" \
            --quiet
        
        echo -e "${CYAN}✅ Traffic split: Green ${stage}%, Blue ${blue_traffic}%${NC}"
        
        # Wait and perform health checks
        if [ "$stage" -lt 100 ]; then
            echo -e "${YELLOW}⏳ Waiting ${STAGE_DURATION}s before next stage...${NC}"
            
            # Perform health checks during the wait
            local check_interval=30
            local checks_per_stage=$((STAGE_DURATION / check_interval))
            local failed_checks=0
            
            for ((i=1; i<=checks_per_stage; i++)); do
                sleep $check_interval
                
                # Get green revision URL
                local green_url=$(get_revision_url "$service_name" "$region" "green")
                if [ -n "$green_url" ]; then
                    if ! health_check "$green_url" "Green-$region-Check-$i"; then
                        ((failed_checks++))
                        if [ $failed_checks -ge $ROLLBACK_THRESHOLD ]; then
                            echo -e "${RED}🚨 Too many health check failures. Initiating rollback...${NC}"
                            rollback_deployment "$service_name" "$region"
                            return 1
                        fi
                    else
                        failed_checks=0  # Reset counter on successful check
                    fi
                fi
            done
        fi
    done
    
    echo -e "${GREEN}🎉 Progressive traffic split completed for $region${NC}"
    return 0
}

# Rollback deployment to previous revision
rollback_deployment() {
    local service_name=$1
    local region=$2
    
    echo -e "${RED}🔙 Rolling back deployment for $service_name in $region${NC}"
    
    # Get the current blue (stable) revision
    local blue_revision=$(gcloud run services describe "$service_name" \
        --region="$region" \
        --project="$PROJECT_ID" \
        --format="value(status.traffic[?tag=='blue'].revisionName)" \
        2>/dev/null | head -n1)
    
    if [ -n "$blue_revision" ]; then
        # Set 100% traffic to blue revision
        gcloud run services update-traffic "$service_name" \
            --region="$region" \
            --project="$PROJECT_ID" \
            --to-revisions="$blue_revision=100" \
            --quiet
        
        echo -e "${GREEN}✅ Rollback completed for $region${NC}"
    else
        echo -e "${YELLOW}⚠️  No blue revision found, manual intervention may be required${NC}"
    fi
}

# Promote green to blue (make it the new stable version)
promote_green_to_blue() {
    local service_name=$1
    local region=$2
    
    echo -e "${PURPLE}🔄 Promoting green to blue for $service_name in $region${NC}"
    
    # Get current green revision
    local green_revision=$(gcloud run services describe "$service_name" \
        --region="$region" \
        --project="$PROJECT_ID" \
        --format="value(status.traffic[?tag=='green'].revisionName)" \
        2>/dev/null | head -n1)
    
    if [ -n "$green_revision" ]; then
        # Update tags: green becomes blue
        gcloud run services update-traffic "$service_name" \
            --region="$region" \
            --project="$PROJECT_ID" \
            --update-tags="blue=$green_revision" \
            --remove-tags="green" \
            --quiet
        
        echo -e "${GREEN}✅ Green promoted to blue in $region${NC}"
    else
        echo -e "${RED}❌ No green revision found in $region${NC}"
        return 1
    fi
}

# Cleanup old revisions
cleanup_old_revisions() {
    local service_name=$1
    local region=$2
    local keep_revisions=5
    
    echo -e "${YELLOW}🧹 Cleaning up old revisions for $service_name in $region${NC}"
    
    # Get all revisions sorted by creation time
    local revisions=$(gcloud run revisions list \
        --service="$service_name" \
        --region="$region" \
        --project="$PROJECT_ID" \
        --format="value(metadata.name)" \
        --sort-by="~metadata.creationTimestamp" \
        --limit=50)
    
    local revision_count=0
    while IFS= read -r revision; do
        if [ -n "$revision" ]; then
            ((revision_count++))
            if [ $revision_count -gt $keep_revisions ]; then
                # Check if revision has traffic (don't delete if it does)
                local traffic=$(gcloud run services describe "$service_name" \
                    --region="$region" \
                    --project="$PROJECT_ID" \
                    --format="value(status.traffic[?revisionName=='$revision'].percent)" \
                    2>/dev/null)
                
                if [ -z "$traffic" ] || [ "$traffic" = "0" ]; then
                    echo -e "${CYAN}🗑️  Deleting old revision: $revision${NC}"
                    gcloud run revisions delete "$revision" \
                        --region="$region" \
                        --project="$PROJECT_ID" \
                        --quiet 2>/dev/null || true
                fi
            fi
        fi
    done <<< "$revisions"
    
    echo -e "${GREEN}✅ Cleanup completed for $region${NC}"
}

# Deploy to both regions with blue-green strategy
deploy_multiregion() {
    echo -e "${PURPLE}🌍 Starting multi-region blue-green deployment${NC}"
    
    # Deploy green revisions to both regions
    if ! deploy_green_revision "$PRIMARY_REGION" "$SERVICE_NAME" "green"; then
        echo -e "${RED}❌ Failed to deploy green revision to $PRIMARY_REGION${NC}"
        exit 1
    fi
    
    if ! deploy_green_revision "$SECONDARY_REGION" "${SERVICE_NAME}-east" "green"; then
        echo -e "${RED}❌ Failed to deploy green revision to $SECONDARY_REGION${NC}"
        exit 1
    fi
    
    # Wait for revisions to be ready
    echo -e "${YELLOW}⏳ Waiting for revisions to be ready...${NC}"
    sleep 30
    
    # Perform initial health checks on green revisions
    local primary_green_url=$(get_revision_url "$SERVICE_NAME" "$PRIMARY_REGION" "green")
    local secondary_green_url=$(get_revision_url "${SERVICE_NAME}-east" "$SECONDARY_REGION" "green")
    
    if [ -n "$primary_green_url" ] && ! health_check "$primary_green_url" "Initial-Primary-Green"; then
        echo -e "${RED}❌ Primary region green revision failed health check${NC}"
        exit 1
    fi
    
    if [ -n "$secondary_green_url" ] && ! health_check "$secondary_green_url" "Initial-Secondary-Green"; then
        echo -e "${RED}❌ Secondary region green revision failed health check${NC}"
        exit 1
    fi
    
    # Progressive traffic split for primary region
    echo -e "${PURPLE}🎯 Starting deployment to primary region ($PRIMARY_REGION)${NC}"
    if ! progressive_traffic_split "$SERVICE_NAME" "$PRIMARY_REGION" "$(get_revision_url "$SERVICE_NAME" "$PRIMARY_REGION" "green" | sed 's/.*\///g')"; then
        echo -e "${RED}❌ Primary region deployment failed${NC}"
        exit 1
    fi
    
    # Progressive traffic split for secondary region
    echo -e "${PURPLE}🎯 Starting deployment to secondary region ($SECONDARY_REGION)${NC}"
    if ! progressive_traffic_split "${SERVICE_NAME}-east" "$SECONDARY_REGION" "$(get_revision_url "${SERVICE_NAME}-east" "$SECONDARY_REGION" "green" | sed 's/.*\///g')"; then
        echo -e "${RED}❌ Secondary region deployment failed${NC}"
        # Rollback primary region as well
        rollback_deployment "$SERVICE_NAME" "$PRIMARY_REGION"
        exit 1
    fi
    
    # Promote green to blue in both regions
    promote_green_to_blue "$SERVICE_NAME" "$PRIMARY_REGION"
    promote_green_to_blue "${SERVICE_NAME}-east" "$SECONDARY_REGION"
    
    # Cleanup old revisions
    cleanup_old_revisions "$SERVICE_NAME" "$PRIMARY_REGION"
    cleanup_old_revisions "${SERVICE_NAME}-east" "$SECONDARY_REGION"
    
    echo -e "${GREEN}🎉 Multi-region blue-green deployment completed successfully!${NC}"
}

# Verify final deployment
verify_deployment() {
    echo -e "${YELLOW}🔍 Verifying final deployment...${NC}"
    
    # Get load balancer IP
    local lb_ip=$(gcloud compute addresses describe lb-ip --global --project="$PROJECT_ID" --format="value(address)")
    
    # Test load balancer health
    if health_check "http://$lb_ip" "LoadBalancer-Final-Check"; then
        echo -e "${GREEN}✅ Load balancer health check passed${NC}"
    else
        echo -e "${YELLOW}⚠️  Load balancer health check failed (may need DNS propagation time)${NC}"
    fi
    
    # Display deployment summary
    echo -e "\n${GREEN}📊 Deployment Summary:${NC}"
    echo -e "${CYAN}Project ID: $PROJECT_ID${NC}"
    echo -e "${CYAN}Image Tag: $IMAGE_TAG${NC}"
    echo -e "${CYAN}Primary Region: $PRIMARY_REGION${NC}"
    echo -e "${CYAN}Secondary Region: $SECONDARY_REGION${NC}"
    echo -e "${CYAN}Load Balancer IP: $lb_ip${NC}"
    
    # Show current traffic allocation
    echo -e "\n${BLUE}Current Traffic Allocation:${NC}"
    echo -e "${YELLOW}Primary Region ($PRIMARY_REGION):${NC}"
    gcloud run services describe "$SERVICE_NAME" \
        --region="$PRIMARY_REGION" \
        --project="$PROJECT_ID" \
        --format="table(status.traffic[].revisionName,status.traffic[].percent)" 2>/dev/null || true
    
    echo -e "${YELLOW}Secondary Region ($SECONDARY_REGION):${NC}"
    gcloud run services describe "${SERVICE_NAME}-east" \
        --region="$SECONDARY_REGION" \
        --project="$PROJECT_ID" \
        --format="table(status.traffic[].revisionName,status.traffic[].percent)" 2>/dev/null || true
}

# Main deployment function
main() {
    echo -e "${GREEN}🚀 Starting Night 48 Multi-Region Blue-Green Deployment${NC}"
    
    check_tools
    validate_infrastructure
    build_and_push_image
    deploy_multiregion
    verify_deployment
    
    echo -e "\n${GREEN}🎉 Night 48 deployment completed successfully!${NC}"
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Monitor application metrics in Cloud Monitoring"
    echo "2. Check error rates and latency across both regions"
    echo "3. Verify load balancer is distributing traffic correctly"
    echo "4. Set up alerting for multi-region health monitoring"
    echo "5. Document the deployment process for future rollouts"
}

# Handle script arguments
case "${1:-}" in
    "check")
        check_tools
        validate_infrastructure
        ;;
    "build")
        build_and_push_image
        ;;
    "deploy")
        deploy_multiregion
        ;;
    "verify")
        verify_deployment
        ;;
    "rollback")
        if [ -z "$2" ]; then
            echo -e "${RED}Usage: $0 rollback <region>${NC}"
            echo "  region: us-central1 or us-east1"
            exit 1
        fi
        if [ "$2" = "us-central1" ]; then
            rollback_deployment "$SERVICE_NAME" "$PRIMARY_REGION"
        elif [ "$2" = "us-east1" ]; then
            rollback_deployment "${SERVICE_NAME}-east" "$SECONDARY_REGION"
        else
            echo -e "${RED}Invalid region. Use us-central1 or us-east1${NC}"
            exit 1
        fi
        ;;
    "cleanup")
        if [ -z "$2" ]; then
            cleanup_old_revisions "$SERVICE_NAME" "$PRIMARY_REGION"
            cleanup_old_revisions "${SERVICE_NAME}-east" "$SECONDARY_REGION"
        else
            if [ "$2" = "us-central1" ]; then
                cleanup_old_revisions "$SERVICE_NAME" "$PRIMARY_REGION"
            elif [ "$2" = "us-east1" ]; then
                cleanup_old_revisions "${SERVICE_NAME}-east" "$SECONDARY_REGION"
            fi
        fi
        ;;
    "")
        main
        ;;
    *)
        echo -e "${RED}Usage: $0 [check|build|deploy|verify|rollback <region>|cleanup [region]]${NC}"
        echo "  check    - Validate tools and infrastructure"
        echo "  build    - Build and push container image only"
        echo "  deploy   - Deploy to both regions with blue-green strategy"
        echo "  verify   - Verify deployment health and status"
        echo "  rollback - Rollback deployment in specified region"
        echo "  cleanup  - Clean up old revisions"
        echo "  (no args) - Run full blue-green deployment"
        exit 1
        ;;
esac 