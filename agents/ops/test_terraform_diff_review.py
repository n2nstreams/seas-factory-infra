"""
Comprehensive test suite for Terraform diff review functionality - Night 44
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from devops_agent import (
    DevOpsAgent, DeploymentConfig, TerraformDiff, TerraformResource,
    TerraformChangeType, SecurityFinding, SecurityLevel, TerraformReview
)

class TestTerraformDiffReview:
    """Test cases for Terraform diff review functionality"""
    
    @pytest.fixture
    def agent(self):
        """Create a DevOps agent for testing"""
        config = DeploymentConfig(
            project_id="test-project",
            environment="test",
            version="1.0.0"
        )
        return DevOpsAgent(config)
    
    @pytest.fixture
    def sample_sql_diff(self):
        """Sample SQL instance diff with security issues"""
        return """
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
    
    @pytest.fixture
    def sample_secure_diff(self):
        """Sample secure diff without issues"""
        return """
+ resource "google_cloud_run_service" "api" {
+   name     = "api-service"
+   location = "us-central1"
+   
+   template {
+     spec {
+       containers {
+         image = "gcr.io/project/api:latest"
+       }
+     }
+   }
+   
+   traffic {
+     percent         = 100
+     latest_revision = true
+   }
+ }
"""
    
    @pytest.fixture
    def sample_complex_diff(self):
        """Complex diff with multiple resources and changes"""
        return """
+ resource "google_compute_instance" "web" {
+   name         = "web-server"
+   machine_type = "e2-medium"
+   zone         = "us-central1-a"
+   
+   boot_disk {
+     initialize_params {
+       image = "debian-cloud/debian-11"
+     }
+   }
+   
+   network_interface {
+     network = "default"
+     access_config {
+       // External IP
+     }
+   }
+   
+   tags = ["web", "production"]
+ }

~ resource "google_storage_bucket" "data" {
~   name     = "data-bucket-v2"
-   location = "US"
+   location = "us-central1"
    
+   uniform_bucket_level_access = true
+   public_access_prevention    = "enforced"
+ }

- resource "google_compute_firewall" "old_rule" {
-   name    = "old-firewall-rule"
-   network = "default"
-   
-   allow {
-     protocol = "tcp"
-     ports    = ["80", "443"]
-   }
-   
-   source_ranges = ["0.0.0.0/0"]
- }
"""

    def test_parse_terraform_diff_create(self, agent, sample_sql_diff):
        """Test parsing of CREATE operations"""
        diff = agent._parse_terraform_diff(sample_sql_diff)
        
        assert len(diff.resources) == 1
        resource = diff.resources[0]
        assert resource.resource_type == "google_sql_database_instance"
        assert resource.resource_name == "main"
        assert resource.change_type == TerraformChangeType.CREATE
        assert diff.raw_diff == sample_sql_diff
    
    def test_parse_terraform_diff_complex(self, agent, sample_complex_diff):
        """Test parsing of complex diff with multiple change types"""
        diff = agent._parse_terraform_diff(sample_complex_diff)
        
        assert len(diff.resources) == 3
        
        # Check CREATE operation
        create_resource = next(r for r in diff.resources if r.change_type == TerraformChangeType.CREATE)
        assert create_resource.resource_type == "google_compute_instance"
        assert create_resource.resource_name == "web"
        
        # Check UPDATE operation
        update_resource = next(r for r in diff.resources if r.change_type == TerraformChangeType.UPDATE)
        assert update_resource.resource_type == "google_storage_bucket"
        assert update_resource.resource_name == "data"
        
        # Check DELETE operation
        delete_resource = next(r for r in diff.resources if r.change_type == TerraformChangeType.DELETE)
        assert delete_resource.resource_type == "google_compute_firewall"
        assert delete_resource.resource_name == "old_rule"
    
    def test_security_analysis_critical_findings(self, agent, sample_sql_diff):
        """Test detection of critical security findings"""
        diff = agent._parse_terraform_diff(sample_sql_diff)
        findings = agent._analyze_security_implications(diff)
        
        # Should detect the 0.0.0.0/0 authorized network
        critical_findings = [f for f in findings if f.severity == SecurityLevel.CRITICAL]
        assert len(critical_findings) > 0
        
        finding = critical_findings[0]
        assert "0.0.0.0/0" in finding.description or "any IP" in finding.description
        assert finding.resource_type == "google_sql_database_instance"
    
    def test_security_analysis_no_findings(self, agent, sample_secure_diff):
        """Test that secure configurations don't trigger false positives"""
        diff = agent._parse_terraform_diff(sample_secure_diff)
        findings = agent._analyze_security_implications(diff)
        
        # Should not have critical findings for this secure configuration
        critical_findings = [f for f in findings if f.severity == SecurityLevel.CRITICAL]
        assert len(critical_findings) == 0
    
    def test_best_practices_violations(self, agent, sample_sql_diff):
        """Test detection of best practices violations"""
        diff = agent._parse_terraform_diff(sample_sql_diff)
        violations = agent._check_best_practices(diff)
        
        # Should detect missing documentation/tags
        assert len(violations) > 0
        assert any("documentation" in v.lower() for v in violations)
    
    def test_cost_implications_analysis(self, agent, sample_complex_diff):
        """Test cost implications analysis"""
        diff = agent._parse_terraform_diff(sample_complex_diff)
        implications = agent._analyze_cost_implications(diff)
        
        # Should identify cost implications for compute instance
        assert len(implications) > 0
        assert any("google_compute_instance" in impl for impl in implications)
    
    def test_calculate_overall_score(self, agent):
        """Test overall score calculation"""
        # Test with no issues
        score = agent._calculate_overall_score([], [])
        assert score == 100.0
        
        # Test with critical finding
        critical_finding = SecurityFinding(
            severity=SecurityLevel.CRITICAL,
            resource_type="test",
            resource_name="test",
            finding_type="test",
            description="test",
            recommendation="test"
        )
        score = agent._calculate_overall_score([critical_finding], [])
        assert score == 70.0  # 100 - 30
        
        # Test with violations
        score = agent._calculate_overall_score([], ["violation1", "violation2"])
        assert score == 90.0  # 100 - 10
    
    def test_should_approve_diff(self, agent):
        """Test approval logic"""
        # Should approve with no critical issues
        assert agent._should_approve_diff([], [])
        
        # Should not approve with critical findings
        critical_finding = SecurityFinding(
            severity=SecurityLevel.CRITICAL,
            resource_type="test",
            resource_name="test",
            finding_type="test",
            description="test",
            recommendation="test"
        )
        assert not agent._should_approve_diff([critical_finding], [])
        
        # Should not approve with too many violations
        violations = [f"violation{i}" for i in range(6)]
        assert not agent._should_approve_diff([], violations)
    
    def test_format_resources_for_prompt(self, agent):
        """Test formatting of resources for LLM prompt"""
        resources = [
            TerraformResource(
                resource_type="google_sql_database_instance",
                resource_name="main",
                change_type=TerraformChangeType.CREATE
            ),
            TerraformResource(
                resource_type="google_storage_bucket",
                resource_name="data",
                change_type=TerraformChangeType.UPDATE
            )
        ]
        
        formatted = agent._format_resources_for_prompt(resources)
        
        assert "CREATE: google_sql_database_instance.main" in formatted
        assert "UPDATE: google_storage_bucket.data" in formatted
    
    def test_extract_recommendations(self, agent):
        """Test extraction of recommendations from LLM response"""
        review_text = """
        ## Summary
        This is a test review.
        
        ## Recommendations
        1. Add proper documentation
        2. Implement security controls
        - Use private networks
        - Enable encryption
        * Add monitoring
        """
        
        recommendations = agent._extract_recommendations(review_text)
        
        assert len(recommendations) >= 3
        assert any("documentation" in r.lower() for r in recommendations)
        assert any("security" in r.lower() for r in recommendations)
    
    def test_extract_summary(self, agent):
        """Test extraction of summary from LLM response"""
        review_text = """
        The changes introduce a new SQL database instance with some security concerns.
        
        Overall the infrastructure changes are reasonable but need security improvements.
        
        ## Detailed Analysis
        ...
        """
        
        summary = agent._extract_summary(review_text)
        
        assert "SQL database instance" in summary
        assert len(summary) > 0
    
    def test_format_github_review_comment(self, agent):
        """Test formatting of GitHub review comment"""
        review = TerraformReview(
            diff_id="test-123",
            pr_number=42,
            overall_score=85.5,
            security_findings=[
                SecurityFinding(
                    severity=SecurityLevel.MEDIUM,
                    resource_type="google_sql_database_instance",
                    resource_name="main",
                    finding_type="security",
                    description="Test security issue",
                    recommendation="Fix it"
                )
            ],
            best_practices_violations=["Missing documentation"],
            cost_implications=["High cost resource"],
            recommendations=["Add security controls", "Improve documentation"],
            approved=True,
            reviewer_notes="Good overall but needs improvements",
            reviewed_at=datetime(2024, 1, 15, 10, 30, 0)
        )
        
        comment = agent._format_github_review_comment(review)
        
        assert "85.5/100" in comment
        assert "✅ Terraform Diff Review" in comment
        assert "🔒 Security Analysis" in comment
        assert "Test security issue" in comment
        assert "Missing documentation" in comment
        assert "High cost resource" in comment
        assert "Add security controls" in comment
        assert "Good overall but needs improvements" in comment
    
    @patch('devops_agent.openai.OpenAI')
    @pytest.mark.asyncio
    async def test_generate_llm_review_success(self, mock_openai, agent):
        """Test successful LLM review generation"""
        # Mock OpenAI response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """
        ## Summary
        This change creates a new SQL database instance.
        
        ## Recommendations
        1. Add backup configuration
        2. Implement network security
        3. Add monitoring
        """
        
        mock_client.chat.completions.create = Mock(return_value=mock_response)
        mock_openai.return_value = mock_client
        
        # Test the review generation
        diff = TerraformDiff(resources=[], raw_diff="test diff")
        review = await agent._generate_llm_review(diff, [])
        
        assert "recommendations" in review
        assert "summary" in review
        assert len(review["recommendations"]) > 0
        assert "backup configuration" in review["recommendations"][0]
    
    @patch('devops_agent.openai.OpenAI')
    @pytest.mark.asyncio
    async def test_generate_llm_review_failure(self, mock_openai, agent):
        """Test LLM review generation failure handling"""
        # Mock OpenAI to raise an exception
        mock_client = Mock()
        mock_client.chat.completions.create = Mock(side_effect=Exception("API Error"))
        mock_openai.return_value = mock_client
        
        # Test the review generation
        diff = TerraformDiff(resources=[], raw_diff="test diff")
        review = await agent._generate_llm_review(diff, [])
        
        assert "recommendations" in review
        assert "LLM review failed" in review["recommendations"][0]
        assert "API Error" in review["summary"]
    
    @patch('devops_agent.create_github_integration')
    @pytest.mark.asyncio
    async def test_review_terraform_diff_complete_flow(self, mock_github, agent, sample_sql_diff):
        """Test complete terraform diff review flow"""
        # Mock GitHub integration
        mock_github_client = Mock()
        mock_github_client.add_pr_comment = Mock()
        mock_github.return_value = mock_github_client
        
        # Mock LLM response
        with patch.object(agent, '_generate_llm_review') as mock_llm:
            mock_llm.return_value = {
                "recommendations": ["Add security controls"],
                "summary": "Good changes with minor issues",
                "full_review": "Detailed review text"
            }
            
            # Perform the review
            review = await agent.review_terraform_diff(sample_sql_diff, pr_number=123)
            
            # Verify the review object
            assert isinstance(review, TerraformReview)
            assert review.pr_number == 123
            assert review.overall_score < 100  # Should have security issues
            assert len(review.security_findings) > 0
            assert not review.approved  # Should not be approved due to critical finding
            assert review.diff_id.startswith("review-")
            
            # Verify GitHub integration was called
            mock_github_client.add_pr_comment.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_review_terraform_diff_no_github(self, agent, sample_secure_diff):
        """Test terraform diff review without GitHub integration"""
        # Test without PR number
        review = await agent.review_terraform_diff(sample_secure_diff)
        
        assert isinstance(review, TerraformReview)
        assert review.pr_number is None
        assert review.overall_score >= 80  # Should be high for secure diff
        assert len(review.security_findings) == 0
        assert review.approved
    
    def test_security_patterns_coverage(self, agent):
        """Test that security patterns cover major resource types"""
        patterns = agent.security_patterns
        
        # Should have patterns for major GCP resources
        assert "google_sql_database_instance" in patterns
        assert "google_compute_instance" in patterns
        assert "google_storage_bucket" in patterns
        assert "google_cloud_run_service" in patterns
        
        # Should have different severity levels
        for resource_type, resource_patterns in patterns.items():
            if resource_patterns:
                assert any(severity in ["critical", "high", "medium", "low"] 
                         for severity in resource_patterns.keys())
    
    def test_best_practices_rules_coverage(self, agent):
        """Test that best practices rules are comprehensive"""
        rules = agent.best_practices_rules
        
        assert len(rules) > 0
        
        # Each rule should have required fields
        for rule in rules:
            assert "pattern" in rule
            assert "message" in rule
            assert "check_function" in rule
    
    def test_check_resource_documentation(self, agent):
        """Test resource documentation checking"""
        # Test with description
        resource_with_desc = 'resource "test" "name" { description = "test" }'
        assert agent._check_resource_documentation(resource_with_desc)
        
        # Test with tags
        resource_with_tags = 'resource "test" "name" { tags = { env = "prod" } }'
        assert agent._check_resource_documentation(resource_with_tags)
        
        # Test without documentation
        resource_without = 'resource "test" "name" { name = "test" }'
        assert not agent._check_resource_documentation(resource_without)
    
    def test_check_variable_documentation(self, agent):
        """Test variable documentation checking"""
        # Test with description and type
        var_with_docs = 'variable "test" { description = "test" type = string }'
        assert agent._check_variable_documentation(var_with_docs)
        
        # Test without description
        var_without_desc = 'variable "test" { type = string }'
        assert not agent._check_variable_documentation(var_without_desc)
        
        # Test without type
        var_without_type = 'variable "test" { description = "test" }'
        assert not agent._check_variable_documentation(var_without_type)


class TestTerraformDiffIntegration:
    """Integration tests for Terraform diff review"""
    
    @pytest.fixture
    def agent(self):
        """Create agent with environment variables"""
        config = DeploymentConfig(
            project_id="test-project",
            environment="test",
            version="1.0.0"
        )
        return DevOpsAgent(config)
    
    @pytest.mark.asyncio
    async def test_end_to_end_review_flow(self, agent):
        """Test complete end-to-end review flow"""
        # Sample diff that should trigger various checks
        diff_content = """
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

+ resource "google_storage_bucket" "data" {
+   name     = "data-bucket"
+   location = "us-central1"
+ }
"""
        
        # Mock LLM to avoid API calls in tests
        with patch.object(agent, '_generate_llm_review') as mock_llm:
            mock_llm.return_value = {
                "recommendations": [
                    "Restrict SQL instance network access",
                    "Add bucket access controls",
                    "Implement backup policies"
                ],
                "summary": "Creates new SQL and storage resources with security concerns",
                "full_review": "Detailed analysis of the infrastructure changes"
            }
            
            # Perform the review
            review = await agent.review_terraform_diff(diff_content)
            
            # Verify comprehensive analysis
            assert len(review.security_findings) > 0
            assert len(review.best_practices_violations) > 0
            assert len(review.cost_implications) > 0
            assert len(review.recommendations) > 0
            assert review.overall_score < 100
            assert not review.approved
            assert review.reviewed_at is not None
    
    def test_multiple_reviews_tracking(self, agent):
        """Test that multiple reviews are tracked correctly"""
        initial_count = len(agent.reviews)
        
        # Create multiple reviews
        for i in range(3):
            diff = f'+ resource "google_storage_bucket" "test{i}" {{ name = "test{i}" }}'
            
            # Mock LLM to avoid API calls
            with patch.object(agent, '_generate_llm_review') as mock_llm:
                mock_llm.return_value = {
                    "recommendations": ["Test recommendation"],
                    "summary": "Test summary",
                    "full_review": "Test review"
                }
                
                asyncio.run(agent.review_terraform_diff(diff))
        
        # Verify all reviews were stored
        assert len(agent.reviews) == initial_count + 3
        
        # Verify each review has unique ID
        review_ids = [r.diff_id for r in agent.reviews[-3:]]
        assert len(set(review_ids)) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 