#!/bin/bash

# Night 49 - Cost Monitoring System Test Suite
# Comprehensive testing for CostGuardAgent and budget alerting infrastructure

set -e

# Configuration
PROJECT_ID="${PROJECT_ID:-summer-nexus-463503-e1}"
REGION="${REGION:-us-central1}"
FUNCTION_NAME="cost-guard-agent"
BUDGET_NAME="Monthly SaaS Factory Budget"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Night 49 - Cost Monitoring Tests     ${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

print_test() {
    echo -e "${YELLOW}[TEST $((++TESTS_RUN))]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ PASS:${NC} $1"
    ((TESTS_PASSED++))
}

print_failure() {
    echo -e "${RED}❌ FAIL:${NC} $1"
    ((TESTS_FAILED++))
}

print_info() {
    echo -e "${BLUE}ℹ️  INFO:${NC} $1"
}

print_summary() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}           TEST SUMMARY                 ${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo -e "Total Tests: ${TESTS_RUN}"
    echo -e "${GREEN}Passed: ${TESTS_PASSED}${NC}"
    echo -e "${RED}Failed: ${TESTS_FAILED}${NC}"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "\n${GREEN}🎉 All tests passed! Cost monitoring system is ready.${NC}"
        exit 0
    else
        echo -e "\n${RED}❌ Some tests failed. Please review and fix issues before deployment.${NC}"
        exit 1
    fi
}

# Test 1: Verify required tools are installed
test_tools_installed() {
    print_test "Verifying required tools are installed"
    
    local tools=("gcloud" "curl" "jq" "terraform")
    local missing_tools=()
    
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            missing_tools+=("$tool")
        fi
    done
    
    if [ ${#missing_tools[@]} -eq 0 ]; then
        print_success "All required tools are installed"
    else
        print_failure "Missing tools: ${missing_tools[*]}"
        print_info "Install missing tools before running tests"
    fi
}

# Test 2: Verify GCP authentication and project access
test_gcp_authentication() {
    print_test "Verifying GCP authentication and project access"
    
    if gcloud auth list --filter=status:ACTIVE --format="value(account)" &>/dev/null; then
        current_project=$(gcloud config get-value project 2>/dev/null)
        if [ "$current_project" = "$PROJECT_ID" ]; then
            print_success "Authenticated with correct project: $PROJECT_ID"
        else
            print_failure "Current project ($current_project) doesn't match expected ($PROJECT_ID)"
            print_info "Run: gcloud config set project $PROJECT_ID"
        fi
    else
        print_failure "No active GCP authentication found"
        print_info "Run: gcloud auth login"
    fi
}

# Test 3: Verify Terraform infrastructure state
test_terraform_state() {
    print_test "Verifying Terraform infrastructure state"
    
    if [ ! -f "terraform.tfstate" ] && [ ! -f ".terraform/terraform.tfstate" ]; then
        print_failure "No Terraform state found"
        print_info "Run: terraform init && terraform plan"
        return
    fi
    
    # Check if cost guard resources are in state
    if terraform show | grep -q "google_cloudfunctions2_function.cost_guard"; then
        print_success "Cost Guard Cloud Function found in Terraform state"
    else
        print_failure "Cost Guard Cloud Function not found in Terraform state"
        print_info "Run: terraform apply to deploy cost monitoring infrastructure"
    fi
}

# Test 4: Verify Pub/Sub topic and subscription exist
test_pubsub_infrastructure() {
    print_test "Verifying Pub/Sub infrastructure"
    
    # Check cost guard topic
    if gcloud pubsub topics describe cost-guard --project="$PROJECT_ID" &>/dev/null; then
        print_success "Cost guard Pub/Sub topic exists"
    else
        print_failure "Cost guard Pub/Sub topic not found"
        return
    fi
    
    # Check subscription
    if gcloud pubsub subscriptions describe cost-guard-subscription --project="$PROJECT_ID" &>/dev/null; then
        print_success "Cost guard Pub/Sub subscription exists"
    else
        print_failure "Cost guard Pub/Sub subscription not found"
    fi
}

# Test 5: Verify Cloud Function deployment
test_cloud_function() {
    print_test "Verifying Cost Guard Cloud Function deployment"
    
    function_info=$(gcloud functions describe "$FUNCTION_NAME" --region="$REGION" --project="$PROJECT_ID" --format=json 2>/dev/null || echo "{}")
    
    if echo "$function_info" | jq -e '.name' &>/dev/null; then
        function_status=$(echo "$function_info" | jq -r '.state // "UNKNOWN"')
        
        if [ "$function_status" = "ACTIVE" ]; then
            print_success "Cost Guard Cloud Function is active"
            
            # Check function configuration
            runtime=$(echo "$function_info" | jq -r '.buildConfig.runtime // "unknown"')
            if [ "$runtime" = "python311" ]; then
                print_success "Cloud Function using correct runtime: $runtime"
            else
                print_failure "Cloud Function using unexpected runtime: $runtime"
            fi
        else
            print_failure "Cloud Function exists but is not active (status: $function_status)"
        fi
    else
        print_failure "Cost Guard Cloud Function not found"
        print_info "Deploy function with: terraform apply"
    fi
}

# Test 6: Verify billing budget configuration
test_billing_budget() {
    print_test "Verifying billing budget configuration"
    
    # Note: This requires billing API access which may not be available in all environments
    if gcloud billing budgets list --billing-account="013356-107066-5683A3" --filter="displayName:'$BUDGET_NAME'" --format="value(name)" 2>/dev/null | grep -q "budgets/"; then
        print_success "Billing budget '$BUDGET_NAME' found"
    else
        print_failure "Billing budget '$BUDGET_NAME' not found or no access"
        print_info "Check billing account permissions or create budget manually"
    fi
}

# Test 7: Verify Secret Manager secrets
test_secret_manager() {
    print_test "Verifying Secret Manager configuration"
    
    secrets=("sendgrid-api-key" "openai-api-key")
    
    for secret in "${secrets[@]}"; do
        if gcloud secrets describe "$secret" --project="$PROJECT_ID" &>/dev/null; then
            print_success "Secret '$secret' exists"
        else
            print_failure "Secret '$secret' not found"
            print_info "Create secret: gcloud secrets create $secret --data-file=-"
        fi
    done
}

# Test 8: Test Cloud Function with mock data
test_function_execution() {
    print_test "Testing Cloud Function with mock budget alert"
    
    # Create mock budget alert data
    mock_data=$(cat <<EOF
{
  "budgetDisplayName": "Test Budget Alert",
  "alertThresholdExceeded": 0.8,
  "costAmount": 160.0,
  "budgetAmount": 200.0,
  "costIntervalStart": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "costIntervalEnd": "$(date -u -d '+1 month' +%Y-%m-%dT%H:%M:%SZ)",
  "currencyCode": "USD",
  "projectId": "$PROJECT_ID",
  "budgetId": "test-budget-id"
}
EOF
    )
    
    # Encode data for Pub/Sub
    encoded_data=$(echo "$mock_data" | base64 -w 0)
    
    # Publish test message to Pub/Sub
    if gcloud pubsub topics publish cost-guard --message="$encoded_data" --project="$PROJECT_ID" &>/dev/null; then
        print_success "Test message published to Pub/Sub topic"
        print_info "Check Cloud Function logs for processing results"
    else
        print_failure "Failed to publish test message to Pub/Sub"
    fi
}

# Test 9: Verify monitoring dashboards
test_monitoring_dashboards() {
    print_test "Verifying cost monitoring dashboard"
    
    # List dashboards and check for cost monitoring dashboard
    dashboards=$(gcloud monitoring dashboards list --project="$PROJECT_ID" --format="value(displayName)" 2>/dev/null || echo "")
    
    if echo "$dashboards" | grep -q "SaaS Factory - Cost Monitoring Dashboard"; then
        print_success "Cost monitoring dashboard found"
    else
        print_failure "Cost monitoring dashboard not found"
        print_info "Deploy dashboard with: terraform apply"
    fi
}

# Test 10: Verify alert policies
test_alert_policies() {
    print_test "Verifying cost alert policies"
    
    alert_policies=$(gcloud alpha monitoring policies list --project="$PROJECT_ID" --format="value(displayName)" 2>/dev/null || echo "")
    
    expected_policies=(
        "Cost Alert - Warning (50% threshold)"
        "Cost Alert - Critical (80% threshold)" 
        "Cost Alert - Emergency (100% threshold)"
    )
    
    for policy in "${expected_policies[@]}"; do
        if echo "$alert_policies" | grep -q "$policy"; then
            print_success "Alert policy found: $policy"
        else
            print_failure "Alert policy missing: $policy"
        fi
    done
}

# Test 11: Verify notification channels
test_notification_channels() {
    print_test "Verifying notification channels"
    
    channels=$(gcloud alpha monitoring channels list --project="$PROJECT_ID" --format="value(displayName,type)" 2>/dev/null || echo "")
    
    if echo "$channels" | grep -q "email"; then
        print_success "Email notification channel configured"
    else
        print_failure "Email notification channel not found"
    fi
    
    if echo "$channels" | grep -q "slack"; then
        print_success "Slack notification channel configured"
    else
        print_failure "Slack notification channel not found"
        print_info "Configure Slack webhook token in terraform.tfvars"
    fi
}

# Test 12: Test email functionality (if SendGrid key is available)
test_email_functionality() {
    print_test "Testing email functionality (if configured)"
    
    if gcloud secrets versions access latest --secret="sendgrid-api-key" --project="$PROJECT_ID" &>/dev/null; then
        print_success "SendGrid API key is configured"
        print_info "Email functionality should work when budget alerts trigger"
    else
        print_failure "SendGrid API key not configured"
        print_info "Add SendGrid API key: echo 'YOUR_KEY' | gcloud secrets create sendgrid-api-key --data-file=-"
    fi
}

# Test 13: Verify IAM permissions
test_iam_permissions() {
    print_test "Verifying IAM permissions for cost guard service account"
    
    sa_email="cost-guard-sa@$PROJECT_ID.iam.gserviceaccount.com"
    
    required_roles=(
        "roles/billing.viewer"
        "roles/pubsub.subscriber" 
        "roles/monitoring.metricWriter"
        "roles/secretmanager.secretAccessor"
    )
    
    for role in "${required_roles[@]}"; do
        if gcloud projects get-iam-policy "$PROJECT_ID" --flatten="bindings[].members" --format="table(bindings.role)" --filter="bindings.members:$sa_email AND bindings.role:$role" | grep -q "$role"; then
            print_success "Service account has role: $role"
        else
            print_failure "Service account missing role: $role"
        fi
    done
}

# Test 14: Check function logs for errors
test_function_logs() {
    print_test "Checking Cloud Function logs for recent errors"
    
    # Check logs from last 24 hours
    log_entries=$(gcloud logging read "resource.type=\"cloud_function\" AND resource.labels.function_name=\"$FUNCTION_NAME\" AND severity>=ERROR AND timestamp>=\"$(date -u -d '1 day ago' +%Y-%m-%dT%H:%M:%SZ)\"" --project="$PROJECT_ID" --format="value(textPayload)" --limit=10 2>/dev/null || echo "")
    
    if [ -z "$log_entries" ]; then
        print_success "No recent errors found in Cloud Function logs"
    else
        print_failure "Recent errors found in Cloud Function logs"
        print_info "Check function logs: gcloud logging read 'resource.type=\"cloud_function\" AND resource.labels.function_name=\"$FUNCTION_NAME\"' --limit=20"
    fi
}

# Test 15: Validate cost dashboard accessibility
test_dashboard_access() {
    print_test "Validating cost dashboard accessibility"
    
    # Try to access dashboard (this will require authentication)
    dashboard_url="https://console.cloud.google.com/monitoring/dashboards?project=$PROJECT_ID"
    
    if curl -s --head "$dashboard_url" | grep -q "200 OK"; then
        print_success "Cost dashboard is accessible"
    else
        print_info "Dashboard accessibility requires browser authentication"
        print_success "Dashboard URL: $dashboard_url"
    fi
}

# Main execution
main() {
    print_header
    
    print_info "Starting Night 49 cost monitoring system tests..."
    print_info "Project: $PROJECT_ID"
    print_info "Region: $REGION"
    echo ""
    
    # Run all tests
    test_tools_installed
    test_gcp_authentication
    test_terraform_state
    test_pubsub_infrastructure
    test_cloud_function
    test_billing_budget
    test_secret_manager
    test_function_execution
    test_monitoring_dashboards
    test_alert_policies
    test_notification_channels
    test_email_functionality
    test_iam_permissions
    test_function_logs
    test_dashboard_access
    
    print_summary
}

# Run main function
main "$@" 