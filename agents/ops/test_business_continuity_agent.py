"""
Test suite for Business Continuity Assurance Agent
Tests all aspects of business continuity validation for Section 8
"""

import asyncio
import json
import os
import pytest
import tempfile
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Import the agent
from business_continuity_agent import (
    BusinessContinuityAgent,
    RollbackStatus,
    DisasterRecoveryStatus,
    SupportTeamStatus,
    DocumentationStatus,
    RollbackTestResult,
    DisasterRecoveryTestResult,
    SupportTeamAssessment,
    DocumentationAssessment,
    BusinessContinuityReport
)


class TestBusinessContinuityAgent:
    """Test class for BusinessContinuityAgent"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.agent = BusinessContinuityAgent()
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        assert self.agent is not None
        assert len(self.agent.modules_to_test) == 10
        assert len(self.agent.dr_components) == 4
        assert self.agent.rollback_timeout == 300
        assert self.agent.disaster_recovery_timeout == 600
    
    def test_modules_to_test_contains_expected_modules(self):
        """Test that expected modules are included for rollback testing"""
        expected_modules = [
            "api_gateway", "orchestrator", "dev_agent", "qa_agent",
            "design_agent", "ops_agent", "billing_agent", "support_agent",
            "marketing_agent", "personalization_agent"
        ]
        
        for module in expected_modules:
            assert module in self.agent.modules_to_test
    
    def test_dr_components_contains_expected_components(self):
        """Test that expected disaster recovery components are included"""
        expected_components = [
            "database_failover", "backup_restore", "service_recovery", "data_migration_rollback"
        ]
        
        for component in expected_components:
            assert component in self.agent.dr_components


class TestRollbackProcedures:
    """Test rollback procedure testing"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.agent = BusinessContinuityAgent()
    
    @pytest.mark.asyncio
    async def test_api_gateway_rollback(self):
        """Test API gateway rollback procedure"""
        result = await self.agent._test_api_gateway_rollback()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_orchestrator_rollback(self):
        """Test orchestrator rollback procedure"""
        result = await self.agent._test_orchestrator_rollback()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_dev_agent_rollback(self):
        """Test dev agent rollback procedure"""
        result = await self.agent._test_dev_agent_rollback()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_qa_agent_rollback(self):
        """Test QA agent rollback procedure"""
        result = await self.agent._test_qa_agent_rollback()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_ops_agent_rollback(self):
        """Test ops agent rollback procedure"""
        result = await self.agent._test_ops_agent_rollback()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_generic_module_rollback(self):
        """Test generic module rollback procedure"""
        result = await self.agent._test_generic_module_rollback("test_module")
        assert result is True
    
    @pytest.mark.asyncio
    async def test_module_rollback_creates_result(self):
        """Test that module rollback testing creates proper result"""
        result = await self.agent._test_module_rollback("test_module")
        
        assert isinstance(result, RollbackTestResult)
        assert result.module_name == "test_module"
        assert result.status in [RollbackStatus.PASSED, RollbackStatus.FAILED]
        assert result.test_duration >= 0
        assert result.success_rate in [0.0, 100.0]
        assert isinstance(result.issues_found, list)
        assert isinstance(result.rollback_time, float)
        assert isinstance(result.validation_passed, bool)
        assert isinstance(result.notes, str)
        assert isinstance(result.tested_at, datetime)


class TestDisasterRecoveryProcedures:
    """Test disaster recovery procedure testing"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.agent = BusinessContinuityAgent()
    
    @pytest.mark.asyncio
    async def test_database_failover(self):
        """Test database failover procedure"""
        result = await self.agent._test_database_failover()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_backup_restore(self):
        """Test backup and restore procedure"""
        result = await self.agent._test_backup_restore()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_service_recovery(self):
        """Test service recovery procedure"""
        result = await self.agent._test_service_recovery()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_data_migration_rollback(self):
        """Test data migration rollback procedure"""
        result = await self.agent._test_data_migration_rollback()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_generic_dr_component(self):
        """Test generic disaster recovery component"""
        result = await self.agent._test_generic_dr_component("test_component")
        assert result is True
    
    @pytest.mark.asyncio
    async def test_dr_component_creates_result(self):
        """Test that DR component testing creates proper result"""
        result = await self.agent._test_dr_component("test_component")
        
        assert isinstance(result, DisasterRecoveryTestResult)
        assert result.component_name == "test_component"
        assert result.status in [DisasterRecoveryStatus.PASSED, DisasterRecoveryStatus.FAILED]
        assert result.test_duration >= 0
        assert isinstance(result.rto_achieved, float)
        assert isinstance(result.rpo_achieved, float)
        assert isinstance(result.backup_restore_time, float)
        assert isinstance(result.failover_time, float)
        assert isinstance(result.issues_found, list)
        assert isinstance(result.notes, str)
        assert isinstance(result.tested_at, datetime)


class TestSupportTeamAssessment:
    """Test support team readiness assessment"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.agent = BusinessContinuityAgent()
    
    @pytest.mark.asyncio
    async def test_support_team_assessment(self):
        """Test support team readiness assessment"""
        await self.agent._assess_support_team_readiness()
        
        assert self.agent.support_team_assessment is not None
        assessment = self.agent.support_team_assessment
        
        assert isinstance(assessment, SupportTeamAssessment)
        assert assessment.team_size == 8
        assert assessment.training_completed == 85.0
        assert assessment.documentation_access is True
        assert assessment.runbook_availability is True
        assert assessment.incident_response_training is True
        assert assessment.escalation_procedures is True
        assert assessment.status == SupportTeamStatus.READY
        assert isinstance(assessment.areas_for_improvement, list)
        assert len(assessment.areas_for_improvement) == 2
        assert assessment.next_training_date is not None
        assert isinstance(assessment.assessed_at, datetime)
    
    def test_support_team_score_calculation(self):
        """Test support team score calculation"""
        # Create mock assessment
        assessment = SupportTeamAssessment(
            team_size=8,
            training_completed=85.0,
            documentation_access=True,
            runbook_availability=True,
            incident_response_training=True,
            escalation_procedures=True,
            status=SupportTeamStatus.READY,
            areas_for_improvement=[],
            next_training_date=datetime.utcnow(),
            assessed_at=datetime.utcnow()
        )
        
        self.agent.support_team_assessment = assessment
        
        score = self.agent._calculate_support_team_score()
        # Base score: 85 + bonus points: 20 = 105, capped at 100
        assert score == 100.0
    
    def test_support_team_score_without_assessment(self):
        """Test support team score calculation without assessment"""
        self.agent.support_team_assessment = None
        
        score = self.agent._calculate_support_team_score()
        assert score == 0.0


class TestDocumentationAssessment:
    """Test documentation completeness assessment"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.agent = BusinessContinuityAgent()
    
    @pytest.mark.asyncio
    async def test_documentation_assessment(self):
        """Test documentation completeness assessment"""
        await self.agent._assess_documentation_completeness()
        
        assert self.agent.documentation_assessment is not None
        assessment = self.agent.documentation_assessment
        
        assert isinstance(assessment, DocumentationAssessment)
        assert assessment.total_documents == 45
        assert assessment.documents_reviewed == 42
        assert assessment.completeness_score == 93.3
        assert isinstance(assessment.last_updated, datetime)
        assert assessment.runbooks_available is True
        assert assessment.procedures_documented is True
        assert assessment.troubleshooting_guides is True
        assert assessment.status == DocumentationStatus.COMPLETE
        assert isinstance(assessment.missing_documents, list)
        assert isinstance(assessment.outdated_documents, list)
        assert isinstance(assessment.assessed_at, datetime)
    
    def test_documentation_score_calculation(self):
        """Test documentation score calculation"""
        # Create mock assessment
        assessment = DocumentationAssessment(
            total_documents=45,
            documents_reviewed=42,
            completeness_score=93.3,
            last_updated=datetime.utcnow(),
            runbooks_available=True,
            procedures_documented=True,
            troubleshooting_guides=True,
            status=DocumentationStatus.COMPLETE,
            missing_documents=[],
            outdated_documents=[],
            assessed_at=datetime.utcnow()
        )
        
        self.agent.documentation_assessment = assessment
        
        score = self.agent._calculate_documentation_score()
        # Base score: 93.3 + bonus points: 15 = 108.3, capped at 100
        assert score == 100.0
    
    def test_documentation_score_without_assessment(self):
        """Test documentation score calculation without assessment"""
        self.agent.documentation_assessment = None
        
        score = self.agent._calculate_documentation_score()
        assert score == 0.0


class TestScoreCalculations:
    """Test score calculation methods"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.agent = BusinessContinuityAgent()
    
    def test_rollback_score_calculation(self):
        """Test rollback score calculation"""
        # No results initially
        score = self.agent._calculate_rollback_score()
        assert score == 0.0
        
        # Add some test results
        self.agent.rollback_results = [
            RollbackTestResult(
                module_name="test1",
                status=RollbackStatus.PASSED,
                test_duration=1.0,
                success_rate=100.0,
                issues_found=[],
                rollback_time=1.0,
                validation_passed=True,
                notes="Test passed"
            ),
            RollbackTestResult(
                module_name="test2",
                status=RollbackStatus.PASSED,
                test_duration=1.0,
                success_rate=100.0,
                issues_found=[],
                rollback_time=1.0,
                validation_passed=True,
                notes="Test passed"
            ),
            RollbackTestResult(
                module_name="test3",
                status=RollbackStatus.FAILED,
                test_duration=1.0,
                success_rate=0.0,
                issues_found=["Test failed"],
                rollback_time=1.0,
                validation_passed=False,
                notes="Test failed"
            )
        ]
        
        score = self.agent._calculate_rollback_score()
        # 2 passed out of 3 = 66.67%
        assert score == pytest.approx(66.67, abs=0.01)
    
    def test_disaster_recovery_score_calculation(self):
        """Test disaster recovery score calculation"""
        # No results initially
        score = self.agent._calculate_disaster_recovery_score()
        assert score == 0.0
        
        # Add some test results
        self.agent.disaster_recovery_results = [
            DisasterRecoveryTestResult(
                component_name="test1",
                status=DisasterRecoveryStatus.PASSED,
                test_duration=1.0,
                rto_achieved=5.0,
                rpo_achieved=0.5,
                backup_restore_time=2.0,
                failover_time=3.0,
                issues_found=[],
                notes="Test passed"
            ),
            DisasterRecoveryTestResult(
                component_name="test2",
                status=DisasterRecoveryStatus.FAILED,
                test_duration=1.0,
                rto_achieved=float('inf'),
                rpo_achieved=float('inf'),
                backup_restore_time=0.0,
                failover_time=0.0,
                issues_found=["Test failed"],
                notes="Test failed"
            )
        ]
        
        score = self.agent._calculate_disaster_recovery_score()
        # 1 passed out of 2 = 50%
        assert score == 50.0


class TestIssueIdentification:
    """Test critical issue identification"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.agent = BusinessContinuityAgent()
    
    def test_identify_critical_issues_no_issues(self):
        """Test critical issue identification with no issues"""
        # Set up successful results
        self.agent.rollback_results = [
            RollbackTestResult(
                module_name="test",
                status=RollbackStatus.PASSED,
                test_duration=1.0,
                success_rate=100.0,
                issues_found=[],
                rollback_time=1.0,
                validation_passed=True,
                notes="Test passed"
            )
        ]
        
        self.agent.disaster_recovery_results = [
            DisasterRecoveryTestResult(
                component_name="test",
                status=DisasterRecoveryStatus.PASSED,
                test_duration=1.0,
                rto_achieved=5.0,
                rpo_achieved=0.5,
                backup_restore_time=2.0,
                failover_time=3.0,
                issues_found=[],
                notes="Test passed"
            )
        ]
        
        self.agent.support_team_assessment = SupportTeamAssessment(
            team_size=8,
            training_completed=90.0,
            documentation_access=True,
            runbook_availability=True,
            incident_response_training=True,
            escalation_procedures=True,
            status=SupportTeamStatus.READY,
            areas_for_improvement=[],
            next_training_date=datetime.utcnow(),
            assessed_at=datetime.utcnow()
        )
        
        self.agent.documentation_assessment = DocumentationAssessment(
            total_documents=45,
            documents_reviewed=45,
            completeness_score=100.0,
            last_updated=datetime.utcnow(),
            runbooks_available=True,
            procedures_documented=True,
            troubleshooting_guides=True,
            status=DocumentationStatus.EXCELLENT,
            missing_documents=[],
            outdated_documents=[],
            assessed_at=datetime.utcnow()
        )
        
        critical_issues = self.agent._identify_critical_issues()
        assert len(critical_issues) == 0
    
    def test_identify_critical_issues_with_issues(self):
        """Test critical issue identification with issues"""
        # Set up failed results
        self.agent.rollback_results = [
            RollbackTestResult(
                module_name="test",
                status=RollbackStatus.FAILED,
                test_duration=1.0,
                success_rate=0.0,
                issues_found=["Test failed"],
                rollback_time=1.0,
                validation_passed=False,
                notes="Test failed"
            )
        ]
        
        self.agent.disaster_recovery_results = [
            DisasterRecoveryTestResult(
                component_name="test",
                status=DisasterRecoveryStatus.FAILED,
                test_duration=1.0,
                rto_achieved=float('inf'),
                rpo_achieved=float('inf'),
                backup_restore_time=0.0,
                failover_time=0.0,
                issues_found=["Test failed"],
                notes="Test failed"
            )
        ]
        
        critical_issues = self.agent._identify_critical_issues()
        assert len(critical_issues) == 2
        assert "1 rollback procedures failed" in critical_issues
        assert "1 disaster recovery procedures failed" in critical_issues


class TestRecommendations:
    """Test recommendation generation"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.agent = BusinessContinuityAgent()
    
    def test_generate_recommendations_no_issues(self):
        """Test recommendation generation with no issues"""
        # Set up successful results
        self.agent.rollback_results = []
        self.agent.disaster_recovery_results = []
        self.agent.support_team_assessment = None
        self.agent.documentation_assessment = None
        
        recommendations = self.agent._generate_recommendations()
        assert len(recommendations) == 0
    
    def test_generate_recommendations_with_issues(self):
        """Test recommendation generation with issues"""
        # Set up failed results
        self.agent.rollback_results = [
            RollbackTestResult(
                module_name="test",
                status=RollbackStatus.FAILED,
                test_duration=1.0,
                success_rate=0.0,
                issues_found=["Test failed"],
                rollback_time=1.0,
                validation_passed=False,
                notes="Test failed"
            )
        ]
        
        self.agent.disaster_recovery_results = [
            DisasterRecoveryTestResult(
                component_name="test",
                status=DisasterRecoveryStatus.FAILED,
                test_duration=1.0,
                rto_achieved=float('inf'),
                rpo_achieved=float('inf'),
                backup_restore_time=0.0,
                failover_time=0.0,
                issues_found=["Test failed"],
                notes="Test failed"
            )
        ]
        
        recommendations = self.agent._generate_recommendations()
        assert len(recommendations) >= 2
        assert "Fix 1 failed rollback procedures" in recommendations
        assert "Fix 1 failed disaster recovery procedures" in recommendations


class TestNextSteps:
    """Test next steps determination"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.agent = BusinessContinuityAgent()
    
    def test_determine_next_steps(self):
        """Test next steps determination"""
        next_steps = self.agent._determine_next_steps()
        
        # Should always include some standard next steps
        assert len(next_steps) >= 4
        assert "Retest all procedures after fixes" in next_steps
        assert "Update runbooks and procedures" in next_steps
        assert "Schedule regular business continuity drills" in next_steps
        assert "Establish continuous improvement process" in next_steps


class TestReportGeneration:
    """Test report generation"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.agent = BusinessContinuityAgent()
    
    @pytest.mark.asyncio
    async def test_generate_assessment_report(self):
        """Test assessment report generation"""
        # Set up some test data
        self.agent.rollback_results = [
            RollbackTestResult(
                module_name="test",
                status=RollbackStatus.PASSED,
                test_duration=1.0,
                success_rate=100.0,
                issues_found=[],
                rollback_time=1.0,
                validation_passed=True,
                notes="Test passed"
            )
        ]
        
        self.agent.disaster_recovery_results = [
            DisasterRecoveryTestResult(
                component_name="test",
                status=DisasterRecoveryStatus.PASSED,
                test_duration=1.0,
                rto_achieved=5.0,
                rpo_achieved=0.5,
                backup_restore_time=2.0,
                failover_time=3.0,
                issues_found=[],
                notes="Test passed"
            )
        ]
        
        # Run assessments
        await self.agent._assess_support_team_readiness()
        await self.agent._assess_documentation_completeness()
        
        # Generate report
        report = await self.agent._generate_assessment_report()
        
        assert isinstance(report, BusinessContinuityReport)
        assert report.report_id is not None
        assert isinstance(report.generated_at, datetime)
        assert isinstance(report.overall_score, float)
        assert report.overall_score >= 0.0
        assert report.overall_score <= 100.0
        assert isinstance(report.rollback_score, float)
        assert isinstance(report.disaster_recovery_score, float)
        assert isinstance(report.support_team_score, float)
        assert isinstance(report.documentation_score, float)
        assert isinstance(report.critical_issues, list)
        assert isinstance(report.recommendations, list)
        assert isinstance(report.next_steps, list)
        assert isinstance(report.production_readiness, bool)


class TestReportSaving:
    """Test report saving functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.agent = BusinessContinuityAgent()
    
    @pytest.mark.asyncio
    async def test_save_report(self):
        """Test report saving to file"""
        # Create a test report
        report = BusinessContinuityReport(
            report_id="test-123",
            generated_at=datetime.utcnow(),
            overall_score=85.0,
            rollback_tests=[],
            rollback_score=90.0,
            disaster_recovery_tests=[],
            disaster_recovery_score=80.0,
            support_team_assessment=None,
            support_team_score=85.0,
            documentation_assessment=None,
            documentation_score=85.0,
            critical_issues=[],
            recommendations=[],
            next_steps=[],
            production_readiness=True
        )
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_filename = f.name
        
        try:
            await self.agent.save_report(report, temp_filename)
            
            # Verify file was created and contains expected data
            assert os.path.exists(temp_filename)
            
            with open(temp_filename, 'r') as f:
                saved_data = json.load(f)
            
            assert saved_data["report_id"] == "test-123"
            assert saved_data["overall_score"] == 85.0
            assert saved_data["production_readiness"] is True
            
        finally:
            # Clean up
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)


class TestCompleteAssessment:
    """Test complete assessment workflow"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.agent = BusinessContinuityAgent()
    
    @pytest.mark.asyncio
    async def test_run_complete_assessment(self):
        """Test complete assessment workflow"""
        report = await self.agent.run_complete_assessment()
        
        assert isinstance(report, BusinessContinuityReport)
        assert report.report_id is not None
        assert isinstance(report.overall_score, float)
        assert report.overall_score >= 0.0
        assert report.overall_score <= 100.0
        
        # Verify all components were tested
        assert len(self.agent.rollback_results) == 10  # All modules
        assert len(self.agent.disaster_recovery_results) == 4  # All DR components
        assert self.agent.support_team_assessment is not None
        assert self.agent.documentation_assessment is not None
        
        # Verify report contains all sections
        assert report.rollback_tests == self.agent.rollback_results
        assert report.disaster_recovery_tests == self.agent.disaster_recovery_results
        assert report.support_team_assessment == self.agent.support_team_assessment
        assert report.documentation_assessment == self.agent.documentation_assessment


# Integration tests
class TestIntegration:
    """Integration tests for business continuity agent"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.agent = BusinessContinuityAgent()
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test end-to-end business continuity workflow"""
        # Run complete assessment
        report = await self.agent.run_complete_assessment()
        
        # Verify report structure
        assert report is not None
        assert isinstance(report, BusinessContinuityReport)
        
        # Verify all scores are calculated
        assert report.rollback_score >= 0.0
        assert report.disaster_recovery_score >= 0.0
        assert report.support_team_score >= 0.0
        assert report.documentation_score >= 0.0
        
        # Verify overall score is reasonable
        assert report.overall_score >= 0.0
        assert report.overall_score <= 100.0
        
        # Verify production readiness logic
        if report.overall_score >= 80.0 and len(report.critical_issues) == 0:
            assert report.production_readiness is True
        else:
            assert report.production_readiness is False
        
        # Verify recommendations and next steps
        assert isinstance(report.recommendations, list)
        assert isinstance(report.next_steps, list)
        
        # Save report
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_filename = f.name
        
        try:
            await self.agent.save_report(report, temp_filename)
            assert os.path.exists(temp_filename)
            
            # Verify saved data matches report
            with open(temp_filename, 'r') as f:
                saved_data = json.load(f)
            
            assert saved_data["overall_score"] == report.overall_score
            assert saved_data["production_readiness"] == report.production_readiness
            
        finally:
            # Clean up
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
