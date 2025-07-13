"""
DevOps Agent - Automated deployment and infrastructure management with Terraform diff review

This agent will handle:
- Deployment orchestration
- Infrastructure provisioning
- CI/CD pipeline management
- Environment management
- Rollback procedures
- LLM-powered Terraform diff review (Night 44)
"""

import logging
import os
import re
import subprocess
import tempfile
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
from pathlib import Path

# Third-party imports
import openai
import httpx
from pydantic import BaseModel, Field

# Import shared components
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from github_integration import (
    create_github_integration, ReviewComment, 
    GitHubIntegration, PullRequestInfo
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAI configuration
openai.api_key = os.getenv("OPENAI_API_KEY")

class TerraformChangeType(Enum):
    """Types of Terraform changes"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    REPLACE = "replace"
    NO_CHANGE = "no-op"

class SecurityLevel(Enum):
    """Security assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class TerraformResource:
    """Represents a Terraform resource in a diff"""
    resource_type: str
    resource_name: str
    change_type: TerraformChangeType
    before_config: Dict[str, Any] = field(default_factory=dict)
    after_config: Dict[str, Any] = field(default_factory=dict)
    change_summary: str = ""

@dataclass
class TerraformDiff:
    """Represents a parsed Terraform diff"""
    resources: List[TerraformResource]
    output_changes: Dict[str, Any] = field(default_factory=dict)
    variable_changes: Dict[str, Any] = field(default_factory=dict)
    provider_changes: Dict[str, Any] = field(default_factory=dict)
    raw_diff: str = ""

@dataclass
class SecurityFinding:
    """Represents a security finding from diff review"""
    severity: SecurityLevel
    resource_type: str
    resource_name: str
    finding_type: str
    description: str
    recommendation: str
    line_number: Optional[int] = None

@dataclass
class TerraformReview:
    """Represents the result of a Terraform diff review"""
    diff_id: str
    pr_number: Optional[int]
    overall_score: float  # 0-100 scale
    security_findings: List[SecurityFinding]
    best_practices_violations: List[str]
    cost_implications: List[str]
    recommendations: List[str]
    approved: bool
    reviewer_notes: str
    reviewed_at: datetime

@dataclass
class DeploymentConfig:
    """Configuration for deployment operations"""
    project_id: str
    environment: str
    version: str
    rollback_enabled: bool = True
    health_check_timeout: int = 300

@dataclass
class DeploymentStatus:
    """Status of deployment operations"""
    deployment_id: str
    status: str
    timestamp: datetime
    version: str
    environment: str
    health_check_passed: bool
    rollback_available: bool

class DevOpsAgent:
    """
    Enhanced DevOps Agent with Terraform diff review capabilities
    """

    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.deployments: List[DeploymentStatus] = []
        self.reviews: List[TerraformReview] = []
        self.github_integration = create_github_integration()
        
        # LLM configuration
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o"
        
        # Security rules and patterns
        self.security_patterns = self._load_security_patterns()
        self.best_practices_rules = self._load_best_practices_rules()

    def _load_security_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load security patterns for different resource types"""
        return {
            "google_sql_database_instance": {
                "critical": [
                    {"pattern": r'"ssl_mode":\s*"ALLOW_UNENCRYPTED_AND_ENCRYPTED"', "message": "SQL instance allows unencrypted connections"},
                    {"pattern": r'"authorized_networks":\s*\[\s*\{\s*"value":\s*"0\.0\.0\.0/0"', "message": "SQL instance allows access from any IP"},
                ],
                "high": [
                    {"pattern": r'"backup_configuration":\s*\[\s*\]', "message": "SQL instance has no backup configuration"},
                    {"pattern": r'"database_version":\s*"POSTGRES_9', "message": "Using outdated PostgreSQL version"},
                ]
            },
            "google_compute_instance": {
                "high": [
                    {"pattern": r'"can_ip_forward":\s*true', "message": "Instance allows IP forwarding"},
                    {"pattern": r'"0\.0\.0\.0/0.*tcp.*22', "message": "SSH access allowed from anywhere"},
                ]
            },
            "google_storage_bucket": {
                "medium": [
                    {"pattern": r'"public_access_prevention":\s*"inherited"', "message": "Bucket public access prevention is inherited"},
                    {"pattern": r'"uniform_bucket_level_access":\s*false', "message": "Bucket uniform access control is disabled"},
                ]
            },
            "google_cloud_run_service": {
                "medium": [
                    {"pattern": r'"allow_unauthenticated":\s*true', "message": "Cloud Run service allows unauthenticated access"},
                ]
            }
        }

    def _load_best_practices_rules(self) -> List[Dict[str, Any]]:
        """Load best practices rules"""
        return [
            {
                "pattern": r'resource\s+"[^"]+"\s+"[^"]+"\s*{[^}]*}',
                "message": "Resource block should include description and tags",
                "check_function": self._check_resource_documentation
            },
            {
                "pattern": r'variable\s+"[^"]+"\s*{[^}]*}',
                "message": "Variable should have description and type",
                "check_function": self._check_variable_documentation
            }
        ]

    def _check_resource_documentation(self, resource_block: str) -> bool:
        """Check if resource has proper documentation"""
        return "description" in resource_block or "tags" in resource_block

    def _check_variable_documentation(self, variable_block: str) -> bool:
        """Check if variable has proper documentation"""
        return "description" in variable_block and "type" in variable_block

    async def review_terraform_diff(self, 
                                   diff_content: str, 
                                   pr_number: Optional[int] = None,
                                   context: Optional[Dict[str, Any]] = None) -> TerraformReview:
        """
        Review Terraform diff using LLM analysis
        
        Args:
            diff_content: The terraform diff content
            pr_number: Optional PR number for GitHub integration
            context: Optional context information
            
        Returns:
            TerraformReview: Comprehensive review results
        """
        self.logger.info(f"Starting Terraform diff review for PR #{pr_number}")
        
        # Parse the diff
        parsed_diff = self._parse_terraform_diff(diff_content)
        
        # Perform security analysis
        security_findings = self._analyze_security_implications(parsed_diff)
        
        # Check best practices
        best_practices_violations = self._check_best_practices(parsed_diff)
        
        # Analyze cost implications
        cost_implications = self._analyze_cost_implications(parsed_diff)
        
        # Generate LLM-powered review
        llm_review = await self._generate_llm_review(parsed_diff, security_findings, context)
        
        # Create review object
        review = TerraformReview(
            diff_id=f"review-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            pr_number=pr_number,
            overall_score=self._calculate_overall_score(security_findings, best_practices_violations),
            security_findings=security_findings,
            best_practices_violations=best_practices_violations,
            cost_implications=cost_implications,
            recommendations=llm_review.get("recommendations", []),
            approved=self._should_approve_diff(security_findings, best_practices_violations),
            reviewer_notes=llm_review.get("summary", ""),
            reviewed_at=datetime.now()
        )
        
        self.reviews.append(review)
        
        # Post review to GitHub if PR provided
        if pr_number and self.github_integration:
            await self._post_github_review(review, diff_content)
        
        return review

    def _parse_terraform_diff(self, diff_content: str) -> TerraformDiff:
        """Parse Terraform diff into structured format"""
        resources = []
        
        # Regex patterns for different change types
        patterns = {
            TerraformChangeType.CREATE: r'^\s*\+\s*resource\s+"([^"]+)"\s+"([^"]+)"',
            TerraformChangeType.DELETE: r'^\s*-\s*resource\s+"([^"]+)"\s+"([^"]+)"',
            TerraformChangeType.UPDATE: r'^\s*~\s*resource\s+"([^"]+)"\s+"([^"]+)"',
            TerraformChangeType.REPLACE: r'^\s*-/\+\s*resource\s+"([^"]+)"\s+"([^"]+)"'
        }
        
        for line in diff_content.split('\n'):
            for change_type, pattern in patterns.items():
                match = re.match(pattern, line)
                if match:
                    resource_type, resource_name = match.groups()
                    resources.append(TerraformResource(
                        resource_type=resource_type,
                        resource_name=resource_name,
                        change_type=change_type,
                        change_summary=line.strip()
                    ))
        
        return TerraformDiff(
            resources=resources,
            raw_diff=diff_content
        )

    def _analyze_security_implications(self, diff: TerraformDiff) -> List[SecurityFinding]:
        """Analyze security implications of the diff"""
        findings = []
        
        for resource in diff.resources:
            resource_patterns = self.security_patterns.get(resource.resource_type, {})
            
            for severity_level, patterns in resource_patterns.items():
                for pattern_config in patterns:
                    if re.search(pattern_config["pattern"], diff.raw_diff):
                        findings.append(SecurityFinding(
                            severity=SecurityLevel(severity_level),
                            resource_type=resource.resource_type,
                            resource_name=resource.resource_name,
                            finding_type="security_violation",
                            description=pattern_config["message"],
                            recommendation=f"Review and fix security configuration for {resource.resource_type}"
                        ))
        
        return findings

    def _check_best_practices(self, diff: TerraformDiff) -> List[str]:
        """Check for best practices violations"""
        violations = []
        
        for resource in diff.resources:
            # Check for missing documentation
            if not self._check_resource_documentation(diff.raw_diff):
                violations.append(f"Resource {resource.resource_name} lacks proper documentation")
            
            # Check for hardcoded values
            if re.search(r':\s*"[^"]*\.(com|org|net|edu)"', diff.raw_diff):
                violations.append(f"Potential hardcoded domain in {resource.resource_name}")
            
            # Check for missing tags
            if resource.resource_type in ["google_compute_instance", "google_storage_bucket"]:
                if "labels" not in diff.raw_diff and "tags" not in diff.raw_diff:
                    violations.append(f"Resource {resource.resource_name} missing labels/tags")
        
        return violations

    def _analyze_cost_implications(self, diff: TerraformDiff) -> List[str]:
        """Analyze potential cost implications"""
        implications = []
        
        expensive_resources = {
            "google_compute_instance": "Compute instances incur hourly costs",
            "google_sql_database_instance": "SQL instances have significant monthly costs",
            "google_storage_bucket": "Storage costs depend on usage patterns",
            "google_cloud_run_service": "Cloud Run costs scale with requests"
        }
        
        for resource in diff.resources:
            if resource.change_type in [TerraformChangeType.CREATE, TerraformChangeType.REPLACE]:
                if resource.resource_type in expensive_resources:
                    implications.append(f"Creating {resource.resource_type} '{resource.resource_name}': {expensive_resources[resource.resource_type]}")
        
        return implications

    async def _generate_llm_review(self, 
                                  diff: TerraformDiff, 
                                  security_findings: List[SecurityFinding],
                                  context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate LLM-powered review of the Terraform diff"""
        
        prompt = self._create_review_prompt(diff, security_findings, context)
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior DevOps engineer reviewing Terraform infrastructure changes. Provide thorough, practical feedback focusing on security, best practices, and operational concerns."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # Parse the response
            review_text = response.choices[0].message.content
            
            # Extract structured information from the response
            recommendations = self._extract_recommendations(review_text)
            summary = self._extract_summary(review_text)
            
            return {
                "recommendations": recommendations,
                "summary": summary,
                "full_review": review_text
            }
            
        except Exception as e:
            self.logger.error(f"Error generating LLM review: {e}")
            return {
                "recommendations": ["LLM review failed - manual review required"],
                "summary": f"Automated review failed: {str(e)}",
                "full_review": ""
            }

    def _create_review_prompt(self, 
                             diff: TerraformDiff, 
                             security_findings: List[SecurityFinding],
                             context: Optional[Dict[str, Any]] = None) -> str:
        """Create a comprehensive prompt for LLM review"""
        
        context_str = ""
        if context:
            context_str = f"\n\nContext: {json.dumps(context, indent=2)}"
        
        security_summary = ""
        if security_findings:
            security_summary = "\n\nSecurity findings identified:\n"
            for finding in security_findings:
                security_summary += f"- {finding.severity.value.upper()}: {finding.description}\n"
        
        prompt = f"""
Please review the following Terraform diff for a cloud infrastructure change:

TERRAFORM DIFF:
{diff.raw_diff}

RESOURCES AFFECTED:
{self._format_resources_for_prompt(diff.resources)}

{security_summary}

{context_str}

Please provide:
1. A summary of the changes and their impact
2. Security assessment and recommendations
3. Best practices compliance
4. Operational considerations
5. Cost implications
6. Specific recommendations for improvement
7. Overall approval recommendation (APPROVE/REJECT/NEEDS_CHANGES)

Format your response clearly with sections and bullet points.
"""
        return prompt

    def _format_resources_for_prompt(self, resources: List[TerraformResource]) -> str:
        """Format resources for the LLM prompt"""
        formatted = []
        for resource in resources:
            formatted.append(f"- {resource.change_type.value.upper()}: {resource.resource_type}.{resource.resource_name}")
        return "\n".join(formatted)

    def _extract_recommendations(self, review_text: str) -> List[str]:
        """Extract recommendations from LLM response"""
        recommendations = []
        
        # Look for numbered or bulleted recommendations
        patterns = [
            r'^\s*\d+\.\s*(.+)$',
            r'^\s*-\s*(.+)$',
            r'^\s*\*\s*(.+)$'
        ]
        
        in_recommendations_section = False
        for line in review_text.split('\n'):
            if re.search(r'recommend|suggest|should|consider', line.lower()):
                in_recommendations_section = True
                continue
            
            if in_recommendations_section:
                for pattern in patterns:
                    match = re.match(pattern, line)
                    if match:
                        recommendations.append(match.group(1).strip())
        
        return recommendations or ["No specific recommendations provided"]

    def _extract_summary(self, review_text: str) -> str:
        """Extract summary from LLM response"""
        lines = review_text.split('\n')
        summary_lines = []
        
        for line in lines[:10]:  # Look at first 10 lines
            if line.strip() and not line.startswith('#'):
                summary_lines.append(line.strip())
        
        return " ".join(summary_lines[:3])  # First 3 meaningful lines

    def _calculate_overall_score(self, 
                               security_findings: List[SecurityFinding], 
                               best_practices_violations: List[str]) -> float:
        """Calculate overall score for the diff"""
        base_score = 100.0
        
        # Deduct points for security findings
        for finding in security_findings:
            if finding.severity == SecurityLevel.CRITICAL:
                base_score -= 30
            elif finding.severity == SecurityLevel.HIGH:
                base_score -= 20
            elif finding.severity == SecurityLevel.MEDIUM:
                base_score -= 10
            elif finding.severity == SecurityLevel.LOW:
                base_score -= 5
        
        # Deduct points for best practices violations
        base_score -= len(best_practices_violations) * 5
        
        return max(0.0, base_score)

    def _should_approve_diff(self, 
                           security_findings: List[SecurityFinding], 
                           best_practices_violations: List[str]) -> bool:
        """Determine if diff should be approved"""
        critical_findings = [f for f in security_findings if f.severity == SecurityLevel.CRITICAL]
        return len(critical_findings) == 0 and len(best_practices_violations) < 5

    async def _post_github_review(self, review: TerraformReview, diff_content: str):
        """Post review comments to GitHub PR"""
        if not self.github_integration:
            self.logger.warning("GitHub integration not available")
            return
        
        try:
            # Create main review comment
            review_comment = self._format_github_review_comment(review)
            
            # Post the review comment
            await self.github_integration.add_pr_comment(
                pr_number=review.pr_number,
                comment=review_comment
            )
            
            # Add inline comments for specific security findings
            for finding in review.security_findings:
                if finding.line_number:
                    inline_comment = ReviewComment(
                        body=f"🔒 **{finding.severity.value.upper()} Security Issue**: {finding.description}\n\n💡 **Recommendation**: {finding.recommendation}",
                        line=finding.line_number,
                        side="RIGHT"
                    )
                    await self.github_integration.add_pr_review_comment(
                        pr_number=review.pr_number,
                        comment=inline_comment
                    )
            
            self.logger.info(f"Posted review comments to PR #{review.pr_number}")
            
        except Exception as e:
            self.logger.error(f"Error posting GitHub review: {e}")

    def _format_github_review_comment(self, review: TerraformReview) -> str:
        """Format review for GitHub comment"""
        
        status_emoji = "✅" if review.approved else "❌"
        score_emoji = "🟢" if review.overall_score >= 80 else "🟡" if review.overall_score >= 60 else "🔴"
        
        comment = f"""## {status_emoji} Terraform Diff Review

**Overall Score**: {score_emoji} {review.overall_score:.1f}/100

### 🔒 Security Analysis
"""
        
        if review.security_findings:
            for finding in review.security_findings:
                severity_emoji = {"critical": "🚨", "high": "⚠️", "medium": "🟡", "low": "ℹ️"}
                comment += f"- {severity_emoji.get(finding.severity.value, '•')} **{finding.severity.value.upper()}**: {finding.description}\n"
        else:
            comment += "- ✅ No security issues identified\n"
        
        comment += f"""
### 📋 Best Practices
"""
        
        if review.best_practices_violations:
            for violation in review.best_practices_violations:
                comment += f"- ❌ {violation}\n"
        else:
            comment += "- ✅ Best practices followed\n"
        
        comment += f"""
### 💰 Cost Implications
"""
        
        if review.cost_implications:
            for implication in review.cost_implications:
                comment += f"- 💸 {implication}\n"
        else:
            comment += "- ✅ No significant cost implications identified\n"
        
        comment += f"""
### 📝 Recommendations
"""
        
        for recommendation in review.recommendations:
            comment += f"- 💡 {recommendation}\n"
        
        comment += f"""
### 🤖 AI Review Summary
{review.reviewer_notes}

---
*Review generated by DevOps Agent on {review.reviewed_at.strftime('%Y-%m-%d %H:%M:%S')} UTC*
"""
        
        return comment

    def deploy_service(self, service_name: str, image_tag: str) -> DeploymentStatus:
        """
        Deploy a service with the specified image tag

        Args:
            service_name: Name of the service to deploy
            image_tag: Container image tag to deploy

        Returns:
            DeploymentStatus: Status of the deployment
        """
        self.logger.info(f"Deploying service {service_name} with image {image_tag}")

        # TODO: Implement actual deployment logic
        # - Update Cloud Run service
        # - Wait for deployment completion
        # - Perform health checks
        # - Update traffic routing

        deployment_status = DeploymentStatus(
            deployment_id=f"deploy-{service_name}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            status="pending",
            timestamp=datetime.now(),
            version=image_tag,
            environment=self.config.environment,
            health_check_passed=False,
            rollback_available=True,
        )

        self.deployments.append(deployment_status)
        return deployment_status

    def rollback_service(
        self, service_name: str, target_version: str
    ) -> DeploymentStatus:
        """
        Rollback a service to a previous version

        Args:
            service_name: Name of the service to rollback
            target_version: Version to rollback to

        Returns:
            DeploymentStatus: Status of the rollback
        """
        self.logger.info(
            f"Rolling back service {service_name} to version {target_version}"
        )

        # TODO: Implement rollback logic
        # - Identify previous healthy version
        # - Update service configuration
        # - Perform health checks
        # - Update monitoring alerts

        rollback_status = DeploymentStatus(
            deployment_id=f"rollback-{service_name}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            status="pending",
            timestamp=datetime.now(),
            version=target_version,
            environment=self.config.environment,
            health_check_passed=False,
            rollback_available=False,
        )

        self.deployments.append(rollback_status)
        return rollback_status

    def check_deployment_health(self, deployment_id: str) -> bool:
        """
        Check the health of a deployment

        Args:
            deployment_id: ID of the deployment to check

        Returns:
            bool: True if deployment is healthy
        """
        self.logger.info(f"Checking health for deployment {deployment_id}")

        # TODO: Implement health check logic
        # - Check service endpoints
        # - Verify database connectivity
        # - Check error rates and latency
        # - Validate resource utilization

        return True

    def get_deployment_status(self, deployment_id: str) -> Optional[DeploymentStatus]:
        """
        Get the status of a specific deployment

        Args:
            deployment_id: ID of the deployment

        Returns:
            DeploymentStatus or None: Status of the deployment
        """
        for deployment in self.deployments:
            if deployment.deployment_id == deployment_id:
                return deployment
        return None

    def list_deployments(self) -> List[DeploymentStatus]:
        """
        List all deployments

        Returns:
            List[DeploymentStatus]: List of all deployments
        """
        return self.deployments

    def setup_monitoring(self, service_name: str) -> bool:
        """
        Setup monitoring for a service

        Args:
            service_name: Name of the service

        Returns:
            bool: True if monitoring setup was successful
        """
        self.logger.info(f"Setting up monitoring for service {service_name}")

        # TODO: Implement monitoring setup
        # - Create uptime checks
        # - Setup alert policies
        # - Configure dashboards
        # - Setup log-based metrics

        return True

    def cleanup_old_deployments(self, retention_days: int = 30) -> int:
        """
        Cleanup old deployment records

        Args:
            retention_days: Number of days to retain deployment records

        Returns:
            int: Number of deployments cleaned up
        """
        self.logger.info(f"Cleaning up deployments older than {retention_days} days")

        # TODO: Implement cleanup logic
        # - Remove old deployment records
        # - Cleanup unused container images
        # - Remove old configuration versions

        return 0


async def main():
    """Main function for testing the enhanced DevOps agent"""
    config = DeploymentConfig(
        project_id="summer-nexus-463503-e1", 
        environment="production", 
        version="0.1.0"
    )

    agent = DevOpsAgent(config)

    # Test deployment
    status = agent.deploy_service("api-backend", "0.1.0")
    print(f"Deployment status: {status}")

    # Test Terraform diff review
    sample_diff = """
    + resource "google_sql_database_instance" "main" {
    +   name             = "main-instance"
    +   database_version = "POSTGRES_13"
    +   region           = "us-central1"
    +   settings {
    +     tier = "db-f1-micro"
    +     ip_configuration {
    +       authorized_networks {
    +         value = "0.0.0.0/0"
    +       }
    +     }
    +   }
    + }
    """
    
    review = await agent.review_terraform_diff(sample_diff)
    print(f"Terraform review: {review}")


if __name__ == "__main__":
    asyncio.run(main())
