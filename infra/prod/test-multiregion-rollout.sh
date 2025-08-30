#!/bin/bash

# Test Script for Night 48 Multi-Region Blue-Green Deployment
# Validates the complete deployment system and infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
PROJECT_ID="summer-nexus-463503-e1"
PRIMARY_REGION="us-central1"
SECONDARY_REGION="us-east1"
TEST_IMAGE_TAG="test-$(date +%Y%m%d-%H%M%S)"

echo -e "${GREEN}🧪 Starting Night 48 Multi-Region Blue-Green Deployment Tests${NC}"

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Test result tracking
test_result() {
    local test_name=$1
    local result=$2
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if [ "$result" -eq 0 ]; then
        echo -e "${GREEN}✅ PASS: $test_name${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ FAIL: $test_name${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# Test 1: Verify script exists and is executable
test_script_executable() {
    echo -e "${BLUE}Test 1: Script Executable${NC}"
    
    if [ -x "./multiregion-rollout.sh" ]; then
        test_result "Script is executable" 0
    else
        test_result "Script is executable" 1
    fi
}

# Test 2: Validate required tools
test_required_tools() {
    echo -e "${BLUE}Test 2: Required Tools${NC}"
    
    local tools=("gcloud" "docker" "terraform" "jq" "curl")
    local missing_tools=0
    
    for tool in "${tools[@]}"; do
        if command -v "$tool" &> /dev/null; then
            echo -e "${GREEN}  ✓ $tool found${NC}"
        else
            echo -e "${RED}  ✗ $tool missing${NC}"
            missing_tools=$((missing_tools + 1))
        fi
    done
    
    test_result "All required tools available" $missing_tools
}

# Test 3: Check GCP project access
test_gcp_access() {
    echo -e "${BLUE}Test 3: GCP Project Access${NC}"
    
    if gcloud projects describe "$PROJECT_ID" &>/dev/null; then
        test_result "GCP project access" 0
    else
        test_result "GCP project access" 1
    fi
}

# Test 4: Verify Cloud Run services exist
test_cloud_run_services() {
    echo -e "${BLUE}Test 4: Cloud Run Services${NC}"
    
    # Test primary region service
    if gcloud run services describe "api-backend" --region="$PRIMARY_REGION" --project="$PROJECT_ID" &>/dev/null; then
        test_result "Primary region service exists" 0
    else
        test_result "Primary region service exists" 1
    fi
    
    # Test secondary region service
    if gcloud run services describe "api-backend-east" --region="$SECONDARY_REGION" --project="$PROJECT_ID" &>/dev/null; then
        test_result "Secondary region service exists" 0
    else
        test_result "Secondary region service exists" 1
    fi
}

# Test 5: Check load balancer configuration
test_load_balancer() {
    echo -e "${BLUE}Test 5: Load Balancer Configuration${NC}"
    
    if gcloud compute global-addresses describe "lb-ip" --project="$PROJECT_ID" &>/dev/null; then
        test_result "Load balancer IP exists" 0
    else
        test_result "Load balancer IP exists" 1
    fi
    
    # Check backend service
    if gcloud compute backend-services describe "api-backend-service" --global --project="$PROJECT_ID" &>/dev/null; then
        test_result "Backend service exists" 0
    else
        test_result "Backend service exists" 1
    fi
}

# Test 6: Verify Artifact Registry
test_artifact_registry() {
    echo -e "${BLUE}Test 6: Artifact Registry${NC}"
    
    if gcloud artifacts repositories describe "saas-factory" --location="$PRIMARY_REGION" --project="$PROJECT_ID" &>/dev/null; then
        test_result "Artifact Registry repository exists" 0
    else
        test_result "Artifact Registry repository exists" 1
    fi
}

# Test 7: Check infrastructure validation
test_infrastructure_validation() {
    echo -e "${BLUE}Test 7: Infrastructure Validation${NC}"
    
    if ./multiregion-rollout.sh check &>/dev/null; then
        test_result "Infrastructure validation passes" 0
    else
        test_result "Infrastructure validation passes" 1
    fi
}

# Test 8: Validate health endpoints
test_health_endpoints() {
    echo -e "${BLUE}Test 8: Health Endpoints${NC}"
    
    # Get service URLs
    local primary_url=$(gcloud run services describe "api-backend" --region="$PRIMARY_REGION" --project="$PROJECT_ID" --format="value(status.url)" 2>/dev/null)
    local secondary_url=$(gcloud run services describe "api-backend-east" --region="$SECONDARY_REGION" --project="$PROJECT_ID" --format="value(status.url)" 2>/dev/null)
    
    # Test primary region health
    if [ -n "$primary_url" ] && curl -f -s --max-time 10 "$primary_url/health" > /dev/null 2>&1; then
        test_result "Primary region health endpoint" 0
    else
        test_result "Primary region health endpoint" 1
    fi
    
    # Test secondary region health
    if [ -n "$secondary_url" ] && curl -f -s --max-time 10 "$secondary_url/health" > /dev/null 2>&1; then
        test_result "Secondary region health endpoint" 0
    else
        test_result "Secondary region health endpoint" 1
    fi
}

# Test 9: Check monitoring configuration
test_monitoring_config() {
    echo -e "${BLUE}Test 9: Monitoring Configuration${NC}"
    
    # Check if monitoring resources exist (this would require terraform state)
    if terraform show -json 2>/dev/null | jq -e '.values.root_module.resources[] | select(.type == "google_monitoring_alert_policy")' > /dev/null 2>&1; then
        test_result "Monitoring alert policies configured" 0
    else
        test_result "Monitoring alert policies configured" 1
    fi
}

# Test 10: Verify traffic allocation functionality
test_traffic_allocation() {
    echo -e "${BLUE}Test 10: Traffic Allocation${NC}"
    
    # Get current traffic allocation for primary service
    local traffic_output=$(gcloud run services describe "api-backend" --region="$PRIMARY_REGION" --project="$PROJECT_ID" --format="value(status.traffic[].percent)" 2>/dev/null)
    
    if [ -n "$traffic_output" ]; then
        test_result "Traffic allocation readable" 0
    else
        test_result "Traffic allocation readable" 1
    fi
}

# Test 11: Check Terraform configuration syntax
test_terraform_syntax() {
    echo -e "${BLUE}Test 11: Terraform Configuration${NC}"
    
    if terraform validate &>/dev/null; then
        test_result "Terraform configuration valid" 0
    else
        test_result "Terraform configuration valid" 1
    fi
}

# Test 12: Validate script help functionality
test_script_help() {
    echo -e "${BLUE}Test 12: Script Help${NC}"
    
    if ./multiregion-rollout.sh --help &>/dev/null || ./multiregion-rollout.sh help &>/dev/null; then
        test_result "Script help available" 0
    else
        # Try invalid argument to see if usage is shown
        if ./multiregion-rollout.sh invalid-arg 2>&1 | grep -q "Usage"; then
            test_result "Script help available" 0
        else
            test_result "Script help available" 1
        fi
    fi
}

# Test 13: Check Cloud Deploy configuration (if enabled)
test_cloud_deploy() {
    echo -e "${BLUE}Test 13: Cloud Deploy Configuration${NC}"
    
    if gcloud deploy delivery-pipelines list --region="$PRIMARY_REGION" --project="$PROJECT_ID" 2>/dev/null | grep -q "api-backend-pipeline"; then
        test_result "Cloud Deploy pipeline exists" 0
    else
        test_result "Cloud Deploy pipeline exists" 1
    fi
}

# Test 14: Verify IAM permissions
test_iam_permissions() {
    echo -e "${BLUE}Test 14: IAM Permissions${NC}"
    
    # Check if current user has necessary permissions
    if gcloud run services list --region="$PRIMARY_REGION" --project="$PROJECT_ID" &>/dev/null; then
        test_result "Cloud Run permissions" 0
    else
        test_result "Cloud Run permissions" 1
    fi
    
    if gcloud compute addresses list --global --project="$PROJECT_ID" &>/dev/null; then
        test_result "Compute permissions" 0
    else
        test_result "Compute permissions" 1
    fi
}

# Test 15: Rollback function validation (dry run)
test_rollback_function() {
    echo -e "${BLUE}Test 15: Rollback Function${NC}"
    
    # Check if rollback function is deployed
    if gcloud functions list --project="$PROJECT_ID" 2>/dev/null | grep -q "auto-rollback-function"; then
        test_result "Auto-rollback function deployed" 0
    else
        test_result "Auto-rollback function deployed" 1
    fi
}

# Run comprehensive test suite
run_comprehensive_tests() {
    echo -e "${YELLOW}Running comprehensive test suite...${NC}\n"
    
    test_script_executable
    test_required_tools
    test_gcp_access
    test_cloud_run_services
    test_load_balancer
    test_artifact_registry
    test_infrastructure_validation
    test_health_endpoints
    test_monitoring_config
    test_traffic_allocation
    test_terraform_syntax
    test_script_help
    test_cloud_deploy
    test_iam_permissions
    test_rollback_function
}

# Test specific functionality
test_specific_function() {
    local function_name=$1
    
    case "$function_name" in
        "tools")
            test_required_tools
            ;;
        "services")
            test_cloud_run_services
            ;;
        "health")
            test_health_endpoints
            ;;
        "monitoring")
            test_monitoring_config
            ;;
        "terraform")
            test_terraform_syntax
            ;;
        *)
            echo -e "${RED}Unknown test function: $function_name${NC}"
            echo "Available functions: tools, services, health, monitoring, terraform"
            exit 1
            ;;
    esac
}

# Generate test report
generate_report() {
    echo -e "\n${BLUE}📊 Test Summary Report${NC}"
    echo -e "${BLUE}=====================${NC}"
    echo -e "Total Tests: $TOTAL_TESTS"
    echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
    echo -e "Failed: ${RED}$FAILED_TESTS${NC}"
    
    if [ $FAILED_TESTS -eq 0 ]; then
        echo -e "\n${GREEN}🎉 All tests passed! The multi-region blue-green deployment system is ready.${NC}"
        exit 0
    else
        echo -e "\n${YELLOW}⚠️  Some tests failed. Please review the issues above before proceeding with deployment.${NC}"
        exit 1
    fi
}

# Performance benchmark (optional)
run_performance_test() {
    echo -e "${BLUE}🚀 Performance Benchmark${NC}"
    
    # Simple load test on health endpoints
    local primary_url=$(gcloud run services describe "api-backend" --region="$PRIMARY_REGION" --project="$PROJECT_ID" --format="value(status.url)" 2>/dev/null)
    
    if [ -n "$primary_url" ]; then
        echo -e "${YELLOW}Running 10 concurrent requests to health endpoint...${NC}"
        
        # Simple parallel curl test
        for i in {1..10}; do
            (curl -s -w "%{time_total}\n" -o /dev/null "$primary_url/health" &)
        done
        wait
        
        echo -e "${GREEN}Performance test completed${NC}"
    else
        echo -e "${RED}Could not get service URL for performance test${NC}"
    fi
}

# Main execution
main() {
    case "${1:-}" in
        "")
            run_comprehensive_tests
            generate_report
            ;;
        "test")
            if [ -n "$2" ]; then
                test_specific_function "$2"
            else
                run_comprehensive_tests
            fi
            generate_report
            ;;
        "performance")
            run_performance_test
            ;;
        "report")
            run_comprehensive_tests
            generate_report
            ;;
        *)
            echo -e "${RED}Usage: $0 [test <function>|performance|report]${NC}"
            echo "  test <function> - Run specific test function"
            echo "  performance     - Run performance benchmark"
            echo "  report         - Run all tests and generate report"
            echo "  (no args)      - Run comprehensive test suite"
            echo ""
            echo "Available test functions:"
            echo "  tools      - Check required tools"
            echo "  services   - Verify Cloud Run services"
            echo "  health     - Test health endpoints"
            echo "  monitoring - Check monitoring configuration"
            echo "  terraform  - Validate Terraform syntax"
            exit 1
            ;;
    esac
}

# Execute main function
main "$@" 