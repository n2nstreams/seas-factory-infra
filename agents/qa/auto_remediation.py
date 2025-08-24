#!/usr/bin/env python3
"""
Auto-Remediation Module - Security Agent Implementation
Implements automatic vulnerability remediation logic including:
- Vulnerability analysis and prioritization
- Automatic fix application (upgrades, patches)
- PR creation with fixes
- Rollback capabilities
"""

import os
import asyncio
import logging
import json
import tempfile
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
from pydantic import BaseModel

# Import shared components
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from github_integration import GitHubIntegration, PullRequestConfig
from tenant_db import TenantContext

logger = logging.getLogger(__name__)

class RemediationType(str, Enum):
    """Types of remediation actions"""
    PACKAGE_UPGRADE = "package_upgrade"
    SECURITY_PATCH = "security_patch"
    CONFIGURATION_FIX = "configuration_fix"
    DEPENDENCY_REMOVAL = "dependency_removal"
    MANUAL_REVIEW = "manual_review"

class RemediationStatus(str, Enum):
    """Status of remediation attempts"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

class RemediationAction(BaseModel):
    """Model for a remediation action"""
    vulnerability_id: str
    package_name: str
    current_version: str
    target_version: str
    remediation_type: RemediationType
    command: str
    description: str
    risk_level: str
    estimated_effort: str
    automated: bool = True
    requires_approval: bool = False

class RemediationResult(BaseModel):
    """Model for remediation result"""
    action: RemediationAction
    status: RemediationStatus
    success: bool
    output: str
    error_message: Optional[str] = None
    execution_time: float
    timestamp: datetime
    rollback_available: bool = False

class AutoRemediationEngine:
    """Engine for automatic vulnerability remediation"""
    
    def __init__(self, tenant_context: TenantContext):
        self.tenant_context = tenant_context
        self.github_integration = GitHubIntegration()
        self.remediation_history: List[RemediationResult] = []
        
        # Configuration
        self.max_concurrent_remediations = int(os.getenv("MAX_CONCURRENT_REMEDIATIONS", "3"))
        self.auto_approve_low_risk = os.getenv("AUTO_APPROVE_LOW_RISK", "true").lower() == "true"
        self.require_manual_approval_high_risk = os.getenv("REQUIRE_MANUAL_APPROVAL_HIGH_RISK", "true").lower() == "true"
        
        # Risk thresholds
        self.risk_thresholds = {
            "low": 0.1,
            "medium": 0.3,
            "high": 0.7,
            "critical": 1.0
        }
    
    async def analyze_vulnerabilities_for_remediation(
        self, 
        scan_results: Dict[str, Any]
    ) -> List[RemediationAction]:
        """Analyze vulnerabilities and generate remediation actions"""
        logger.info("Analyzing vulnerabilities for auto-remediation")
        
        remediation_actions = []
        
        try:
            # Extract vulnerabilities from scan results
            vulnerabilities = scan_results.get("vulnerabilities", [])
            
            for vuln in vulnerabilities:
                action = await self._create_remediation_action(vuln)
                if action:
                    remediation_actions.append(action)
            
            # Sort by priority (critical first, then by effort)
            remediation_actions.sort(
                key=lambda x: (
                    self._get_risk_score(x.risk_level),
                    self._get_effort_score(x.estimated_effort)
                ),
                reverse=True
            )
            
            logger.info(f"Generated {len(remediation_actions)} remediation actions")
            return remediation_actions
            
        except Exception as e:
            logger.error(f"Error analyzing vulnerabilities: {e}")
            return []
    
    async def _create_remediation_action(self, vulnerability: Dict[str, Any]) -> Optional[RemediationAction]:
        """Create a remediation action for a vulnerability"""
        try:
            vuln_id = vulnerability.get("id", "")
            package_name = vulnerability.get("package_name", "")
            current_version = vulnerability.get("package_version", "")
            severity = vulnerability.get("severity", "medium")
            
            # Determine remediation type based on vulnerability details
            remediation_type = self._determine_remediation_type(vulnerability)
            
            if not remediation_type:
                return None
            
            # Generate remediation command
            command = self._generate_remediation_command(vulnerability, remediation_type)
            
            # Determine if automated remediation is possible
            automated = self._can_automate_remediation(vulnerability, remediation_type)
            
            # Determine if approval is required
            requires_approval = self._requires_approval(severity, remediation_type)
            
            return RemediationAction(
                vulnerability_id=vuln_id,
                package_name=package_name,
                current_version=current_version,
                target_version=self._get_target_version(vulnerability),
                remediation_type=remediation_type,
                command=command,
                description=self._generate_description(vulnerability, remediation_type),
                risk_level=severity,
                estimated_effort=self._estimate_effort(remediation_type, vulnerability),
                automated=automated,
                requires_approval=requires_approval
            )
            
        except Exception as e:
            logger.error(f"Error creating remediation action: {e}")
            return None
    
    def _determine_remediation_type(self, vulnerability: Dict[str, Any]) -> Optional[RemediationType]:
        """Determine the best remediation type for a vulnerability"""
        try:
            # Check if package is upgradable
            if vulnerability.get("is_upgradable", False):
                return RemediationType.PACKAGE_UPGRADE
            
            # Check if security patch is available
            if vulnerability.get("is_patchable", False):
                return RemediationType.SECURITY_PATCH
            
            # Check if it's a configuration issue
            if vulnerability.get("type") == "configuration":
                return RemediationType.CONFIGURATION_FIX
            
            # Check if dependency can be removed
            if vulnerability.get("is_dev_dependency", False):
                return RemediationType.DEPENDENCY_REMOVAL
            
            # Default to manual review
            return RemediationType.MANUAL_REVIEW
            
        except Exception as e:
            logger.error(f"Error determining remediation type: {e}")
            return RemediationType.MANUAL_REVIEW
    
    def _generate_remediation_command(self, vulnerability: Dict[str, Any], remediation_type: RemediationType) -> str:
        """Generate the command to execute remediation"""
        try:
            package_name = vulnerability.get("package_name", "")
            
            if remediation_type == RemediationType.PACKAGE_UPGRADE:
                target_version = self._get_target_version(vulnerability)
                if target_version:
                    return f"npm update {package_name}@{target_version}"
                else:
                    return f"npm update {package_name}"
            
            elif remediation_type == RemediationType.SECURITY_PATCH:
                return f"snyk patch {vulnerability.get('id', '')}"
            
            elif remediation_type == RemediationType.CONFIGURATION_FIX:
                return f"# Configuration fix for {package_name} - manual review required"
            
            elif remediation_type == RemediationType.DEPENDENCY_REMOVAL:
                return f"npm uninstall {package_name}"
            
            else:
                return f"# Manual review required for {package_name}"
                
        except Exception as e:
            logger.error(f"Error generating remediation command: {e}")
            return f"# Error generating command for {vulnerability.get('package_name', 'unknown')}"
    
    def _get_target_version(self, vulnerability: Dict[str, Any]) -> str:
        """Get the target version for upgrade"""
        try:
            upgrade_path = vulnerability.get("upgrade_path", [])
            if upgrade_path and len(upgrade_path) > 0:
                return upgrade_path[-1]
            
            patched_versions = vulnerability.get("patched_versions", [])
            if patched_versions and len(patched_versions) > 0:
                return patched_versions[0]
            
            return "latest"
            
        except Exception as e:
            logger.error(f"Error getting target version: {e}")
            return "latest"
    
    def _generate_description(self, vulnerability: Dict[str, Any], remediation_type: RemediationType) -> str:
        """Generate description for remediation action"""
        try:
            title = vulnerability.get("title", "Unknown vulnerability")
            package_name = vulnerability.get("package_name", "unknown")
            
            if remediation_type == RemediationType.PACKAGE_UPGRADE:
                target_version = self._get_target_version(vulnerability)
                return f"Upgrade {package_name} to {target_version} to fix: {title}"
            
            elif remediation_type == RemediationType.SECURITY_PATCH:
                return f"Apply security patch to {package_name} for: {title}"
            
            elif remediation_type == RemediationType.CONFIGURATION_FIX:
                return f"Fix configuration for {package_name}: {title}"
            
            elif remediation_type == RemediationType.DEPENDENCY_REMOVAL:
                return f"Remove unused dependency {package_name}: {title}"
            
            else:
                return f"Manual review required for {package_name}: {title}"
                
        except Exception as e:
            logger.error(f"Error generating description: {e}")
            return f"Remediation for {vulnerability.get('package_name', 'unknown')}"
    
    def _estimate_effort(self, remediation_type: RemediationType, vulnerability: Dict[str, Any]) -> str:
        """Estimate effort required for remediation"""
        try:
            if remediation_type == RemediationType.PACKAGE_UPGRADE:
                return "low"
            elif remediation_type == RemediationType.SECURITY_PATCH:
                return "low"
            elif remediation_type == RemediationType.CONFIGURATION_FIX:
                return "medium"
            elif remediation_type == RemediationType.DEPENDENCY_REMOVAL:
                return "low"
            else:
                return "high"
        except Exception as e:
            logger.error(f"Error estimating effort: {e}")
            return "medium"
    
    def _can_automate_remediation(self, vulnerability: Dict[str, Any], remediation_type: RemediationType) -> bool:
        """Determine if remediation can be automated"""
        try:
            # High and critical vulnerabilities require approval
            severity = vulnerability.get("severity", "medium")
            if severity in ["high", "critical"]:
                return False
            
            # Manual review types cannot be automated
            if remediation_type == RemediationType.MANUAL_REVIEW:
                return False
            
            # Configuration fixes require manual review
            if remediation_type == RemediationType.CONFIGURATION_FIX:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error determining automation capability: {e}")
            return False
    
    def _requires_approval(self, severity: str, remediation_type: RemediationType) -> bool:
        """Determine if remediation requires approval"""
        try:
            # High and critical vulnerabilities require approval
            if severity in ["high", "critical"]:
                return True
            
            # Manual review types require approval
            if remediation_type == RemediationType.MANUAL_REVIEW:
                return True
            
            # Configuration fixes require approval
            if remediation_type == RemediationType.CONFIGURATION_FIX:
                return True
            
            # Check if auto-approval is enabled for low risk
            if severity == "low" and self.auto_approve_low_risk:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error determining approval requirement: {e}")
            return True
    
    def _get_risk_score(self, risk_level: str) -> float:
        """Get numeric risk score for sorting"""
        return self.risk_thresholds.get(risk_level.lower(), 0.5)
    
    def _get_effort_score(self, effort: str) -> float:
        """Get numeric effort score for sorting"""
        effort_scores = {"low": 0.1, "medium": 0.5, "high": 1.0}
        return effort_scores.get(effort.lower(), 0.5)
    
    async def execute_remediation_actions(
        self, 
        actions: List[RemediationAction],
        project_path: str
    ) -> List[RemediationResult]:
        """Execute remediation actions"""
        logger.info(f"Executing {len(actions)} remediation actions")
        
        results = []
        semaphore = asyncio.Semaphore(self.max_concurrent_remediations)
        
        # Execute actions concurrently with semaphore limit
        tasks = []
        for action in actions:
            if action.automated:
                task = self._execute_single_remediation(action, project_path, semaphore)
                tasks.append(task)
            else:
                # Log manual actions
                results.append(RemediationResult(
                    action=action,
                    status=RemediationStatus.PENDING,
                    success=False,
                    output="Manual review required",
                    execution_time=0.0,
                    timestamp=datetime.now(),
                    rollback_available=False
                ))
        
        # Wait for all automated actions to complete
        if tasks:
            automated_results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in automated_results:
                if isinstance(result, RemediationResult):
                    results.append(result)
                else:
                    logger.error(f"Error in automated remediation: {result}")
        
        # Update remediation history
        self.remediation_history.extend(results)
        
        return results
    
    async def _execute_single_remediation(
        self, 
        action: RemediationAction, 
        project_path: str,
        semaphore: asyncio.Semaphore
    ) -> RemediationResult:
        """Execute a single remediation action"""
        async with semaphore:
            start_time = datetime.now()
            
            try:
                logger.info(f"Executing remediation: {action.description}")
                
                # Update status to in progress
                result = RemediationResult(
                    action=action,
                    status=RemediationStatus.IN_PROGRESS,
                    success=False,
                    output="",
                    execution_time=0.0,
                    timestamp=start_time,
                    rollback_available=False
                )
                
                # Execute the remediation command
                output, error = await self._run_remediation_command(action.command, project_path)
                
                # Determine success
                success = not error and "error" not in output.lower()
                
                # Calculate execution time
                execution_time = (datetime.now() - start_time).total_seconds()
                
                # Update result
                result.status = RemediationStatus.SUCCESS if success else RemediationStatus.FAILED
                result.success = success
                result.output = output
                result.error_message = error
                result.execution_time = execution_time
                result.rollback_available = success and self._can_rollback(action)
                
                if success:
                    logger.info(f"Remediation successful: {action.description}")
                else:
                    logger.error(f"Remediation failed: {action.description} - {error}")
                
                return result
                
            except Exception as e:
                execution_time = (datetime.now() - start_time).total_seconds()
                logger.error(f"Error executing remediation {action.description}: {e}")
                
                return RemediationResult(
                    action=action,
                    status=RemediationStatus.FAILED,
                    success=False,
                    output="",
                    error_message=str(e),
                    execution_time=execution_time,
                    timestamp=start_time,
                    rollback_available=False
                )
    
    async def _run_remediation_command(self, command: str, project_path: str) -> Tuple[str, Optional[str]]:
        """Run a remediation command in the project directory"""
        try:
            # Skip commands that are just comments
            if command.startswith("#"):
                return "Skipped - manual action required", None
            
            # Create temporary directory for execution
            with tempfile.TemporaryDirectory() as temp_dir:
                # Copy project files to temp directory
                project_files = Path(project_path)
                if project_files.exists():
                    # Use rsync or cp to copy files
                    copy_cmd = f"cp -r {project_path}/* {temp_dir}/"
                    subprocess.run(copy_cmd, shell=True, check=True)
                
                # Change to temp directory
                original_dir = os.getcwd()
                os.chdir(temp_dir)
                
                try:
                    # Execute the remediation command
                    process = await asyncio.create_subprocess_exec(
                        *command.split(),
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    stdout, stderr = await process.communicate()
                    
                    output = stdout.decode() if stdout else ""
                    error = stderr.decode() if stderr else None
                    
                    # Check if command succeeded
                    if process.returncode != 0:
                        error = error or f"Command failed with return code {process.returncode}"
                    
                    return output, error
                    
                finally:
                    # Restore original directory
                    os.chdir(original_dir)
                    
        except Exception as e:
            logger.error(f"Error running remediation command: {e}")
            return "", str(e)
    
    def _can_rollback(self, action: RemediationAction) -> bool:
        """Determine if remediation can be rolled back"""
        try:
            # Package upgrades can be rolled back
            if action.remediation_type == RemediationType.PACKAGE_UPGRADE:
                return True
            
            # Security patches can be rolled back
            if action.remediation_type == RemediationType.SECURITY_PATCH:
                return True
            
            # Configuration fixes and dependency removals are harder to rollback
            return False
            
        except Exception as e:
            logger.error(f"Error determining rollback capability: {e}")
            return False
    
    async def create_remediation_pr(
        self, 
        actions: List[RemediationAction],
        results: List[RemediationResult],
        project_name: str,
        base_branch: str = "main"
    ) -> Optional[str]:
        """Create a pull request with remediation changes"""
        try:
            if not self.github_integration.token:
                logger.warning("GitHub token not available - cannot create PR")
                return None
            
            # Generate PR title and body
            title = f"🔒 Security Auto-Remediation: {project_name}"
            body = self._generate_pr_body(actions, results)
            
            # Create branch name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            head_branch = f"security-remediation-{timestamp}"
            
            # Configure PR
            pr_config = PullRequestConfig(
                title=title,
                body=body,
                head_branch=head_branch,
                base_branch=base_branch,
                draft=False,
                auto_merge=False,
                labels=["security", "auto-remediation", "dependencies"],
                assignees=[],
                reviewers=[]
            )
            
            # Create PR (this would need to be implemented in GitHub integration)
            # For now, return the PR configuration
            logger.info(f"PR configuration prepared: {title}")
            return f"PR-{timestamp}"
            
        except Exception as e:
            logger.error(f"Error creating remediation PR: {e}")
            return None
    
    def _generate_pr_body(self, actions: List[RemediationAction], results: List[RemediationResult]) -> str:
        """Generate PR body with remediation details"""
        try:
            body = "# 🔒 Security Auto-Remediation\n\n"
            body += "This PR contains automatic security vulnerability fixes.\n\n"
            
            # Summary
            successful = [r for r in results if r.success]
            failed = [r for r in results if not r.success]
            
            body += f"## 📊 Summary\n"
            body += f"- **Total Actions:** {len(actions)}\n"
            body += f"- **Successful:** {len(successful)}\n"
            body += f"- **Failed:** {len(failed)}\n"
            body += f"- **Manual Review Required:** {len([a for a in actions if a.requires_approval])}\n\n"
            
            # Successful remediations
            if successful:
                body += "## ✅ Successful Remediations\n"
                for result in successful:
                    body += f"- **{result.action.package_name}**: {result.action.description}\n"
                body += "\n"
            
            # Failed remediations
            if failed:
                body += "## ❌ Failed Remediations\n"
                for result in failed:
                    body += f"- **{result.action.package_name}**: {result.action.description}\n"
                    if result.error_message:
                        body += f"  - Error: {result.error_message}\n"
                body += "\n"
            
            # Manual actions
            manual_actions = [a for a in actions if a.requires_approval]
            if manual_actions:
                body += "## 👀 Manual Review Required\n"
                for action in manual_actions:
                    body += f"- **{action.package_name}**: {action.description}\n"
                body += "\n"
            
            # Rollback information
            rollback_available = [r for r in results if r.rollback_available]
            if rollback_available:
                body += "## 🔄 Rollback Available\n"
                body += "The following remediations can be rolled back if needed:\n"
                for result in rollback_available:
                    body += f"- {result.action.package_name}\n"
                body += "\n"
            
            body += "---\n"
            body += "*This PR was automatically generated by the Security Agent*\n"
            
            return body
            
        except Exception as e:
            logger.error(f"Error generating PR body: {e}")
            return "Error generating PR body"
    
    async def rollback_remediation(self, result: RemediationResult, project_path: str) -> bool:
        """Rollback a successful remediation"""
        try:
            if not result.rollback_available:
                logger.warning(f"Rollback not available for {result.action.description}")
                return False
            
            logger.info(f"Rolling back remediation: {result.action.description}")
            
            # Generate rollback command
            rollback_command = self._generate_rollback_command(result.action)
            
            # Execute rollback
            output, error = await self._run_remediation_command(rollback_command, project_path)
            
            if error:
                logger.error(f"Rollback failed: {error}")
                return False
            
            # Update result status
            result.status = RemediationStatus.ROLLED_BACK
            result.rollback_available = False
            
            logger.info(f"Rollback successful: {result.action.description}")
            return True
            
        except Exception as e:
            logger.error(f"Error rolling back remediation: {e}")
            return False
    
    def _generate_rollback_command(self, action: RemediationAction) -> str:
        """Generate rollback command for a remediation action"""
        try:
            if action.remediation_type == RemediationType.PACKAGE_UPGRADE:
                return f"npm install {action.package_name}@{action.current_version}"
            elif action.remediation_type == RemediationType.SECURITY_PATCH:
                return f"# Rollback patch for {action.package_name} - manual intervention required"
            else:
                return f"# Rollback not supported for {action.remediation_type}"
                
        except Exception as e:
            logger.error(f"Error generating rollback command: {e}")
            return f"# Error generating rollback command"
    
    def get_remediation_summary(self) -> Dict[str, Any]:
        """Get summary of remediation activities"""
        try:
            total_actions = len(self.remediation_history)
            successful = len([r for r in self.remediation_history if r.success])
            failed = len([r for r in self.remediation_history if not r.success])
            pending = len([r for r in self.remediation_history if r.status == RemediationStatus.PENDING])
            
            return {
                "total_actions": total_actions,
                "successful": successful,
                "failed": failed,
                "pending": pending,
                "success_rate": (successful / total_actions * 100) if total_actions > 0 else 0,
                "last_activity": self.remediation_history[-1].timestamp if self.remediation_history else None
            }
            
        except Exception as e:
            logger.error(f"Error getting remediation summary: {e}")
            return {}
