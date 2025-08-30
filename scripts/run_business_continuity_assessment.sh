#!/bin/bash

# Business Continuity Assessment Script - Section 8
# Runs comprehensive business continuity validation and generates reports

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPORTS_DIR="$PROJECT_ROOT/reports"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$REPORTS_DIR/business_continuity_assessment_${TIMESTAMP}.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# Create reports directory if it doesn't exist
mkdir -p "$REPORTS_DIR"

# Function to check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed or not in PATH"
        exit 1
    fi
    
    # Check if required Python packages are available
    if ! python3 -c "import fastapi, pydantic" &> /dev/null; then
        log_warning "Required Python packages not found. Installing..."
        pip3 install fastapi pydantic
    fi
    
    # Check if the business continuity agent exists
    if [ ! -f "$PROJECT_ROOT/agents/ops/business_continuity_agent.py" ]; then
        log_error "Business continuity agent not found at expected location"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Function to run business continuity assessment
run_assessment() {
    log_info "Starting business continuity assessment..."
    
    cd "$PROJECT_ROOT/agents/ops"
    
    # Create a simple test script to run the assessment
    cat > run_assessment.py << 'EOF'
#!/usr/bin/env python3
"""
Simple script to run business continuity assessment
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from business_continuity_agent import BusinessContinuityAgent

async def main():
    """Run the business continuity assessment"""
    print("🚀 Starting Business Continuity Assessment...")
    
    try:
        # Create agent instance
        agent = BusinessContinuityAgent()
        
        # Run complete assessment
        report = await agent.run_complete_assessment()
        
        # Save report
        timestamp = report.generated_at.strftime("%Y%m%d_%H%M%S")
        filename = f"business_continuity_report_{timestamp}.json"
        await agent.save_report(report, filename)
        
        # Print summary
        print(f"\n📊 ASSESSMENT COMPLETED SUCCESSFULLY")
        print(f"📋 Report ID: {report.report_id}")
        print(f"📈 Overall Score: {report.overall_score:.1f}/100")
        print(f"🚀 Production Ready: {'✅ YES' if report.production_readiness else '❌ NO'}")
        print(f"📁 Report saved to: {filename}")
        
        # Print detailed scores
        print(f"\n📊 DETAILED SCORES:")
        print(f"   Rollback Procedures: {report.rollback_score:.1f}/100")
        print(f"   Disaster Recovery: {report.disaster_recovery_score:.1f}/100")
        print(f"   Support Team: {report.support_team_score:.1f}/100")
        print(f"   Documentation: {report.documentation_score:.1f}/100")
        
        # Print critical issues if any
        if report.critical_issues:
            print(f"\n🚨 CRITICAL ISSUES:")
            for issue in report.critical_issues:
                print(f"   ❌ {issue}")
        else:
            print(f"\n✅ No critical issues found")
        
        # Print recommendations
        if report.recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in report.recommendations:
                print(f"   📝 {rec}")
        
        # Print next steps
        if report.next_steps:
            print(f"\n🔄 NEXT STEPS:")
            for step in report.next_steps:
                print(f"   ➡️ {step}")
        
        return report
        
    except Exception as e:
        print(f"❌ Assessment failed: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(main())
EOF
    
    # Run the assessment
    if python3 run_assessment.py; then
        log_success "Business continuity assessment completed successfully"
        
        # Find the generated report
        REPORT_FILE=$(find . -name "business_continuity_report_*.json" -type f | head -1)
        if [ -n "$REPORT_FILE" ]; then
            # Move report to reports directory
            mv "$REPORT_FILE" "$REPORTS_DIR/"
            log_success "Report moved to: $REPORTS_DIR/$(basename "$REPORT_FILE")"
        fi
        
        # Clean up
        rm -f run_assessment.py
        
    else
        log_error "Business continuity assessment failed"
        rm -f run_assessment.py
        exit 1
    fi
}

# Function to run tests
run_tests() {
    log_info "Running business continuity agent tests..."
    
    cd "$PROJECT_ROOT/agents/ops"
    
    # Check if pytest is available
    if ! command -v pytest &> /dev/null; then
        log_warning "pytest not found. Installing..."
        pip3 install pytest pytest-asyncio
    fi
    
    # Run tests
    if pytest test_business_continuity_agent.py -v; then
        log_success "All tests passed"
    else
        log_warning "Some tests failed - check output above"
    fi
}

# Function to generate summary report
generate_summary() {
    log_info "Generating assessment summary..."
    
    # Find the latest report
    LATEST_REPORT=$(find "$REPORTS_DIR" -name "business_continuity_report_*.json" -type f | sort | tail -1)
    
    if [ -n "$LATEST_REPORT" ]; then
        # Extract key information from the report
        python3 -c "
import json
import sys

try:
    with open('$LATEST_REPORT', 'r') as f:
        data = json.load(f)
    
    print('📊 BUSINESS CONTINUITY ASSESSMENT SUMMARY')
    print('=' * 50)
    print(f'📅 Assessment Date: {data.get(\"generated_at\", \"Unknown\")}')
    print(f'🆔 Report ID: {data.get(\"report_id\", \"Unknown\")}')
    print(f'📈 Overall Score: {data.get(\"overall_score\", 0):.1f}/100')
    print(f'🚀 Production Ready: {\"✅ YES\" if data.get(\"production_readiness\", False) else \"❌ NO\"}')
    print()
    print('📊 DETAILED SCORES:')
    print(f'   Rollback Procedures: {data.get(\"rollback_score\", 0):.1f}/100')
    print(f'   Disaster Recovery: {data.get(\"disaster_recovery_score\", 0):.1f}/100')
    print(f'   Support Team: {data.get(\"support_team_score\", 0):.1f}/100')
    print(f'   Documentation: {data.get(\"documentation_score\", 0):.1f}/100')
    print()
    
    critical_issues = data.get('critical_issues', [])
    if critical_issues:
        print('🚨 CRITICAL ISSUES:')
        for issue in critical_issues:
            print(f'   ❌ {issue}')
    else:
        print('✅ No critical issues found')
    print()
    
    recommendations = data.get('recommendations', [])
    if recommendations:
        print('💡 RECOMMENDATIONS:')
        for rec in recommendations:
            print(f'   📝 {rec}')
    print()
    
    next_steps = data.get('next_steps', [])
    if next_steps:
        print('🔄 NEXT STEPS:')
        for step in next_steps:
            print(f'   ➡️ {step}')
    
except Exception as e:
    print(f'Error generating summary: {e}')
    sys.exit(1)
"
        
        # Save summary to file
        SUMMARY_FILE="$REPORTS_DIR/business_continuity_summary_${TIMESTAMP}.txt"
        python3 -c "
import json

with open('$LATEST_REPORT', 'r') as f:
    data = json.load(f)

with open('$SUMMARY_FILE', 'w') as f:
    f.write('BUSINESS CONTINUITY ASSESSMENT SUMMARY\\n')
    f.write('=' * 50 + '\\n')
    f.write(f'Assessment Date: {data.get(\"generated_at\", \"Unknown\")}\\n')
    f.write(f'Report ID: {data.get(\"report_id\", \"Unknown\")}\\n')
    f.write(f'Overall Score: {data.get(\"overall_score\", 0):.1f}/100\\n')
    f.write(f'Production Ready: {\"YES\" if data.get(\"production_readiness\", False) else \"NO\"}\\n\\n')
    
    f.write('DETAILED SCORES:\\n')
    f.write(f'  Rollback Procedures: {data.get(\"rollback_score\", 0):.1f}/100\\n')
    f.write(f'  Disaster Recovery: {data.get(\"disaster_recovery_score\", 0):.1f}/100\\n')
    f.write(f'  Support Team: {data.get(\"support_team_score\", 0):.1f}/100\\n')
    f.write(f'  Documentation: {data.get(\"documentation_score\", 0):.1f}/100\\n\\n')
    
    critical_issues = data.get('critical_issues', [])
    if critical_issues:
        f.write('CRITICAL ISSUES:\\n')
        for issue in critical_issues:
            f.write(f'  - {issue}\\n')
        f.write('\\n')
    
    recommendations = data.get('recommendations', [])
    if recommendations:
        f.write('RECOMMENDATIONS:\\n')
        for rec in recommendations:
            f.write(f'  - {rec}\\n')
        f.write('\\n')
    
    next_steps = data.get('next_steps', [])
    if next_steps:
        f.write('NEXT STEPS:\\n')
        for step in next_steps:
            f.write(f'  - {step}\\n')
"
        
        log_success "Summary saved to: $SUMMARY_FILE"
        
    else
        log_warning "No assessment report found to generate summary"
    fi
}

# Function to show help
show_help() {
    cat << EOF
Business Continuity Assessment Script - Section 8

Usage: $0 [OPTIONS]

OPTIONS:
    -h, --help          Show this help message
    -t, --test          Run tests only
    -a, --assess        Run assessment only
    -s, --summary       Generate summary only
    -f, --full          Run full assessment with tests and summary (default)

EXAMPLES:
    $0                    # Run full assessment
    $0 --test            # Run tests only
    $0 --assess          # Run assessment only
    $0 --summary         # Generate summary only

DESCRIPTION:
    This script runs a comprehensive business continuity assessment for Section 8
    of the pre-decommission checklist. It tests rollback procedures, disaster
    recovery, support team readiness, and documentation completeness.

    The assessment covers:
    - Rollback procedures for all modules
    - Disaster recovery procedures
    - Support team readiness assessment
    - Documentation completeness validation

    Results are saved to the reports/ directory with timestamps.

EOF
}

# Main execution
main() {
    log_info "🚀 Business Continuity Assessment Script - Section 8"
    log_info "Timestamp: $TIMESTAMP"
    log_info "Project Root: $PROJECT_ROOT"
    log_info "Reports Directory: $REPORTS_DIR"
    log_info "Log File: $LOG_FILE"
    
    # Parse command line arguments
    RUN_TESTS=false
    RUN_ASSESSMENT=false
    GENERATE_SUMMARY=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -t|--test)
                RUN_TESTS=true
                shift
                ;;
            -a|--assess)
                RUN_ASSESSMENT=true
                shift
                ;;
            -s|--summary)
                GENERATE_SUMMARY=true
                shift
                ;;
            -f|--full)
                RUN_TESTS=true
                RUN_ASSESSMENT=true
                GENERATE_SUMMARY=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # If no specific options provided, run everything
    if [ "$RUN_TESTS" = false ] && [ "$RUN_ASSESSMENT" = false ] && [ "$GENERATE_SUMMARY" = false ]; then
        RUN_TESTS=true
        RUN_ASSESSMENT=true
        GENERATE_SUMMARY=true
    fi
    
    # Check prerequisites
    check_prerequisites
    
    # Run tests if requested
    if [ "$RUN_TESTS" = true ]; then
        run_tests
    fi
    
    # Run assessment if requested
    if [ "$RUN_ASSESSMENT" = true ]; then
        run_assessment
    fi
    
    # Generate summary if requested
    if [ "$GENERATE_SUMMARY" = true ]; then
        generate_summary
    fi
    
    log_success "🎉 Business continuity assessment completed successfully!"
    log_info "Check the reports directory for detailed results: $REPORTS_DIR"
    log_info "Log file: $LOG_FILE"
}

# Run main function
main "$@"
