#!/usr/bin/env python3
"""
GitHub Integration Module - Night 38 Implementation
Shared GitHub API integration for auto-commit workflow:
- DevAgent opens PRs
- ReviewAgent comments  
- Orchestrator merges on green
"""

import os
import asyncio
import base64
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path
import logging

try:
    import httpx
    from pydantic import BaseModel, Field
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    logging.warning("GitHub integration dependencies not available")

logger = logging.getLogger(__name__)

class GitHubFile(BaseModel):
    """Model for a file to be added to a GitHub repository"""
    path: str = Field(..., description="File path in repository")
    content: str = Field(..., description="File content")
    encoding: str = Field(default="utf-8", description="Content encoding")
    is_binary: bool = Field(default=False, description="Whether file is binary")

class PullRequestConfig(BaseModel):
    """Configuration for creating a pull request"""
    title: str = Field(..., description="PR title")
    body: str = Field(..., description="PR description")
    head_branch: str = Field(..., description="Source branch name")
    base_branch: str = Field(default="main", description="Target branch name")
    draft: bool = Field(default=False, description="Create as draft PR")
    auto_merge: bool = Field(default=False, description="Enable auto-merge")
    labels: List[str] = Field(default_factory=list, description="PR labels")
    assignees: List[str] = Field(default_factory=list, description="PR assignees")
    reviewers: List[str] = Field(default_factory=list, description="PR reviewers")

class CommitInfo(BaseModel):
    """Information about a commit"""
    sha: str
    message: str
    author: Dict[str, str]
    url: str
    date: datetime

class PullRequestInfo(BaseModel):
    """Information about a pull request"""
    number: int
    title: str
    body: str
    state: str
    head_branch: str
    base_branch: str
    url: str
    draft: bool
    mergeable: Optional[bool]
    merged: bool
    created_at: datetime
    updated_at: datetime
    commits_url: str
    review_comments_url: str

class ReviewComment(BaseModel):
    """Model for a pull request review comment"""
    body: str = Field(..., description="Comment content")
    path: Optional[str] = Field(None, description="File path for inline comments")
    line: Optional[int] = Field(None, description="Line number for inline comments")
    side: str = Field(default="RIGHT", description="Side of diff (LEFT/RIGHT)")

class GitHubIntegration:
    """GitHub API integration for auto-commit workflow"""
    
    def __init__(self, token: Optional[str] = None, repo: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.repo = repo or os.getenv("GITHUB_REPOSITORY")
        
        if not self.token:
            logger.warning("GitHub token not provided - GitHub integration disabled")
            
        if not self.repo:
            logger.warning("GitHub repository not specified")
            
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "SaaS-Factory-Agent/1.0"
        }
        
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
    
    def _get_repo_info(self) -> tuple[str, str]:
        """Extract owner and repo name from repository string"""
        if not self.repo:
            raise ValueError("GitHub repository not configured")
        
        parts = self.repo.split("/")
        if len(parts) != 2:
            raise ValueError(f"Invalid repository format: {self.repo}")
        
        return parts[0], parts[1]
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make authenticated GitHub API request"""
        if not self.token:
            raise ValueError("GitHub token not configured")
        
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                timeout=30.0
            )
            
            if response.status_code >= 400:
                logger.error(f"GitHub API error: {response.status_code} - {response.text}")
                response.raise_for_status()
            
            return response.json()
    
    async def get_repository_info(self) -> Dict[str, Any]:
        """Get basic repository information"""
        owner, repo = self._get_repo_info()
        return await self._make_request("GET", f"/repos/{owner}/{repo}")
    
    async def get_branch_info(self, branch: str) -> Dict[str, Any]:
        """Get information about a specific branch"""
        owner, repo = self._get_repo_info()
        return await self._make_request("GET", f"/repos/{owner}/{repo}/branches/{branch}")
    
    async def create_branch(self, branch_name: str, from_branch: str = "main") -> Dict[str, Any]:
        """Create a new branch from existing branch"""
        owner, repo = self._get_repo_info()
        
        # Get the SHA of the source branch
        source_info = await self.get_branch_info(from_branch)
        source_sha = source_info["commit"]["sha"]
        
        # Create new branch
        data = {
            "ref": f"refs/heads/{branch_name}",
            "sha": source_sha
        }
        
        return await self._make_request("POST", f"/repos/{owner}/{repo}/git/refs", data)
    
    async def delete_branch(self, branch_name: str) -> bool:
        """Delete a branch"""
        try:
            owner, repo = self._get_repo_info()
            await self._make_request("DELETE", f"/repos/{owner}/{repo}/git/refs/heads/{branch_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting branch {branch_name}: {e}")
            return False
    
    async def create_or_update_file(
        self, 
        file_path: str, 
        content: str, 
        commit_message: str,
        branch: str = "main",
        encoding: str = "utf-8"
    ) -> Dict[str, Any]:
        """Create or update a single file in the repository"""
        owner, repo = self._get_repo_info()
        
        # Encode content
        if encoding == "base64":
            encoded_content = content
        else:
            encoded_content = base64.b64encode(content.encode(encoding)).decode("ascii")
        
        # Check if file exists to get SHA for updates
        file_sha = None
        try:
            existing_file = await self._make_request(
                "GET", 
                f"/repos/{owner}/{repo}/contents/{file_path}",
                params={"ref": branch}
            )
            file_sha = existing_file["sha"]
        except httpx.HTTPStatusError as e:
            if e.response.status_code != 404:
                raise
        
        # Prepare data
        data = {
            "message": commit_message,
            "content": encoded_content,
            "branch": branch
        }
        
        if file_sha:
            data["sha"] = file_sha
        
        return await self._make_request(
            "PUT", 
            f"/repos/{owner}/{repo}/contents/{file_path}", 
            data
        )
    
    async def create_multiple_files(
        self,
        files: List[GitHubFile],
        commit_message: str,
        branch: str
    ) -> List[Dict[str, Any]]:
        """Create or update multiple files in sequence"""
        results = []
        
        for file in files:
            try:
                result = await self.create_or_update_file(
                    file_path=file.path,
                    content=file.content,
                    commit_message=f"{commit_message} - {file.path}",
                    branch=branch,
                    encoding=file.encoding
                )
                results.append(result)
                
                # Small delay between requests to avoid rate limiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error creating file {file.path}: {e}")
                results.append({"error": str(e), "file": file.path})
        
        return results
    
    async def create_pull_request(self, config: PullRequestConfig) -> PullRequestInfo:
        """Create a new pull request"""
        owner, repo = self._get_repo_info()
        
        data = {
            "title": config.title,
            "body": config.body,
            "head": config.head_branch,
            "base": config.base_branch,
            "draft": config.draft
        }
        
        # Create the PR
        pr_data = await self._make_request("POST", f"/repos/{owner}/{repo}/pulls", data)
        
        # Add labels if specified
        if config.labels:
            await self.add_pr_labels(pr_data["number"], config.labels)
        
        # Add assignees if specified
        if config.assignees:
            await self.add_pr_assignees(pr_data["number"], config.assignees)
        
        # Request reviewers if specified
        if config.reviewers:
            await self.request_pr_reviewers(pr_data["number"], config.reviewers)
        
        # Enable auto-merge if requested
        if config.auto_merge:
            await self.enable_auto_merge(pr_data["number"])
        
        return PullRequestInfo(
            number=pr_data["number"],
            title=pr_data["title"],
            body=pr_data["body"],
            state=pr_data["state"],
            head_branch=pr_data["head"]["ref"],
            base_branch=pr_data["base"]["ref"],
            url=pr_data["html_url"],
            draft=pr_data["draft"],
            mergeable=pr_data.get("mergeable"),
            merged=pr_data["merged"],
            created_at=datetime.fromisoformat(pr_data["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(pr_data["updated_at"].replace("Z", "+00:00")),
            commits_url=pr_data["commits_url"],
            review_comments_url=pr_data["review_comments_url"]
        )
    
    async def get_pull_request(self, pr_number: int) -> PullRequestInfo:
        """Get information about a pull request"""
        owner, repo = self._get_repo_info()
        pr_data = await self._make_request("GET", f"/repos/{owner}/{repo}/pulls/{pr_number}")
        
        return PullRequestInfo(
            number=pr_data["number"],
            title=pr_data["title"],
            body=pr_data["body"],
            state=pr_data["state"],
            head_branch=pr_data["head"]["ref"],
            base_branch=pr_data["base"]["ref"],
            url=pr_data["html_url"],
            draft=pr_data["draft"],
            mergeable=pr_data.get("mergeable"),
            merged=pr_data["merged"],
            created_at=datetime.fromisoformat(pr_data["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(pr_data["updated_at"].replace("Z", "+00:00")),
            commits_url=pr_data["commits_url"],
            review_comments_url=pr_data["review_comments_url"]
        )
    
    async def add_pr_comment(self, pr_number: int, comment: str) -> Dict[str, Any]:
        """Add a comment to a pull request"""
        owner, repo = self._get_repo_info()
        data = {"body": comment}
        return await self._make_request("POST", f"/repos/{owner}/{repo}/issues/{pr_number}/comments", data)
    
    async def add_pr_review_comment(
        self, 
        pr_number: int, 
        comment: ReviewComment,
        commit_sha: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add a review comment to a pull request"""
        owner, repo = self._get_repo_info()
        
        data = {
            "body": comment.body,
            "side": comment.side
        }
        
        if comment.path:
            data["path"] = comment.path
        
        if comment.line:
            data["line"] = comment.line
        
        if commit_sha:
            data["commit_id"] = commit_sha
        
        return await self._make_request("POST", f"/repos/{owner}/{repo}/pulls/{pr_number}/comments", data)
    
    async def add_pr_labels(self, pr_number: int, labels: List[str]) -> Dict[str, Any]:
        """Add labels to a pull request"""
        owner, repo = self._get_repo_info()
        data = {"labels": labels}
        return await self._make_request("POST", f"/repos/{owner}/{repo}/issues/{pr_number}/labels", data)
    
    async def add_pr_assignees(self, pr_number: int, assignees: List[str]) -> Dict[str, Any]:
        """Add assignees to a pull request"""
        owner, repo = self._get_repo_info()
        data = {"assignees": assignees}
        return await self._make_request("POST", f"/repos/{owner}/{repo}/issues/{pr_number}/assignees", data)
    
    async def request_pr_reviewers(self, pr_number: int, reviewers: List[str]) -> Dict[str, Any]:
        """Request reviewers for a pull request"""
        owner, repo = self._get_repo_info()
        data = {"reviewers": reviewers}
        return await self._make_request("POST", f"/repos/{owner}/{repo}/pulls/{pr_number}/requested_reviewers", data)
    
    async def enable_auto_merge(self, pr_number: int, merge_method: str = "squash") -> Dict[str, Any]:
        """Enable auto-merge for a pull request"""
        owner, repo = self._get_repo_info()
        data = {"merge_method": merge_method}
        
        # Use GraphQL API for auto-merge (requires different headers)
        headers = {
            **self.headers,
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Note: This is a simplified version. Full implementation would use GraphQL API
        # For now, we'll just return a placeholder
        return {"message": "Auto-merge would be enabled via GraphQL API"}
    
    async def merge_pull_request(
        self, 
        pr_number: int, 
        commit_title: Optional[str] = None,
        commit_message: Optional[str] = None,
        merge_method: str = "squash"
    ) -> Dict[str, Any]:
        """Merge a pull request"""
        owner, repo = self._get_repo_info()
        
        data = {"merge_method": merge_method}
        
        if commit_title:
            data["commit_title"] = commit_title
        
        if commit_message:
            data["commit_message"] = commit_message
        
        return await self._make_request("PUT", f"/repos/{owner}/{repo}/pulls/{pr_number}/merge", data)
    
    async def get_pr_commits(self, pr_number: int) -> List[CommitInfo]:
        """Get commits for a pull request"""
        owner, repo = self._get_repo_info()
        commits_data = await self._make_request("GET", f"/repos/{owner}/{repo}/pulls/{pr_number}/commits")
        
        commits = []
        for commit_data in commits_data:
            commits.append(CommitInfo(
                sha=commit_data["sha"],
                message=commit_data["commit"]["message"],
                author=commit_data["commit"]["author"],
                url=commit_data["html_url"],
                date=datetime.fromisoformat(commit_data["commit"]["author"]["date"].replace("Z", "+00:00"))
            ))
        
        return commits
    
    async def get_pr_status_checks(self, pr_number: int) -> Dict[str, Any]:
        """Get status checks for a pull request"""
        pr_info = await self.get_pull_request(pr_number)
        owner, repo = self._get_repo_info()
        
        # Get the latest commit SHA
        commits = await self.get_pr_commits(pr_number)
        if not commits:
            return {"status": "no_commits", "checks": []}
        
        latest_commit_sha = commits[-1].sha
        
        # Get combined status
        combined_status = await self._make_request(
            "GET", 
            f"/repos/{owner}/{repo}/commits/{latest_commit_sha}/status"
        )
        
        # Get check runs (newer GitHub checks API)
        try:
            check_runs = await self._make_request(
                "GET",
                f"/repos/{owner}/{repo}/commits/{latest_commit_sha}/check-runs"
            )
        except Exception as e:
            logger.warning(f"Could not fetch check runs: {e}")
            check_runs = {"check_runs": []}
        
        return {
            "combined_status": combined_status,
            "check_runs": check_runs,
            "latest_commit_sha": latest_commit_sha
        }
    
    async def is_pr_ready_to_merge(self, pr_number: int) -> Dict[str, Any]:
        """Check if a pull request is ready to merge"""
        pr_info = await self.get_pull_request(pr_number)
        status_checks = await self.get_pr_status_checks(pr_number)
        
        # Check basic PR state
        if pr_info.state != "open":
            return {"ready": False, "reason": f"PR is {pr_info.state}"}
        
        if pr_info.draft:
            return {"ready": False, "reason": "PR is a draft"}
        
        if not pr_info.mergeable:
            return {"ready": False, "reason": "PR has merge conflicts"}
        
        # Check status checks
        combined_status = status_checks.get("combined_status", {})
        if combined_status.get("state") == "failure":
            return {"ready": False, "reason": "Status checks failed"}
        
        if combined_status.get("state") == "pending":
            return {"ready": False, "reason": "Status checks pending"}
        
        # Check individual check runs
        check_runs = status_checks.get("check_runs", {}).get("check_runs", [])
        for check in check_runs:
            if check.get("status") != "completed":
                return {"ready": False, "reason": f"Check '{check.get('name')}' not completed"}
            
            if check.get("conclusion") not in ["success", "neutral", "skipped"]:
                return {"ready": False, "reason": f"Check '{check.get('name')}' failed"}
        
        return {
            "ready": True, 
            "reason": "All checks passed",
            "pr_info": pr_info,
            "status_checks": status_checks
        }

# Utility functions for agents
def create_github_integration(token: Optional[str] = None, repo: Optional[str] = None) -> Optional[GitHubIntegration]:
    """Create GitHubIntegration instance if dependencies are available"""
    if not DEPENDENCIES_AVAILABLE:
        logger.warning("GitHub integration dependencies not available")
        return None
    
    return GitHubIntegration(token=token, repo=repo)

def generate_branch_name(prefix: str, identifier: str) -> str:
    """Generate a unique branch name"""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{prefix}/{identifier}-{timestamp}"

def generate_pr_title(module_name: str, action: str = "Add") -> str:
    """Generate a descriptive PR title"""
    return f"{action} {module_name} module - Auto-generated code"

def generate_pr_body(
    module_name: str, 
    description: str,
    dev_agent_request_id: Optional[str] = None,
    review_results: Optional[Dict] = None
) -> str:
    """Generate a comprehensive PR description"""
    body_parts = [
        f"## 🤖 Auto-generated: {module_name}",
        "",
        f"**Description:** {description}",
        "",
        "### 📋 Generated Content",
        "This pull request was automatically created by the DevAgent as part of the AI SaaS Factory pipeline.",
        ""
    ]
    
    if dev_agent_request_id:
        body_parts.extend([
            f"**DevAgent Request ID:** `{dev_agent_request_id}`",
            ""
        ])
    
    body_parts.extend([
        "### ✅ Review Process",
        "- [ ] Code generated by DevAgent",
        "- [ ] Tests executed by ReviewAgent", 
        "- [ ] Quality checks passed",
        "- [ ] Ready for auto-merge",
        ""
    ])
    
    if review_results:
        body_parts.extend([
            "### 📊 Review Results",
            f"- **Quality Score:** {review_results.get('quality_score', 'N/A')}/100",
            f"- **Test Pass Rate:** {review_results.get('pass_rate', 'N/A')}%",
            f"- **Coverage:** {review_results.get('coverage', 'N/A')}%",
            ""
        ])
    
    body_parts.extend([
        "### 🔄 Auto-commit Workflow",
        "This PR is part of the Night 38 auto-commit implementation:",
        "1. **DevAgent** generates code and opens this PR",
        "2. **ReviewAgent** runs tests and provides feedback",
        "3. **Orchestrator** merges when all checks pass",
        "",
        "---",
        "*🤖 This PR was created automatically by the AI SaaS Factory*"
    ])
    
    return "\n".join(body_parts) 