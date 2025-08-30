#!/usr/bin/env python3
"""
Night 38 Auto-Commit Workflow Demo
Demonstrates the complete workflow: DevAgent -> ReviewAgent -> Auto-merge
"""

import asyncio
from datetime import datetime

# Mock GitHub integration for demo
class MockGitHubIntegration:
    def __init__(self):
        self.prs = {}
        self.pr_counter = 1
        
    async def create_pull_request(self, config):
        pr_number = self.pr_counter
        self.pr_counter += 1
        
        self.prs[pr_number] = {
            "number": pr_number,
            "title": config.title,
            "body": config.body,
            "head_branch": config.head_branch,
            "base_branch": config.base_branch,
            "state": "open",
            "mergeable": True,
            "labels": config.labels,
            "created_at": datetime.now()
        }
        
        return type('PR', (), {
            'number': pr_number,
            'title': config.title,
            'body': config.body,
            'url': f"https://github.com/test/repo/pull/{pr_number}",
            'head_branch': config.head_branch,
            'base_branch': config.base_branch,
            'state': 'open',
            'draft': False,
            'mergeable': True,
            'merged': False,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'commits_url': f"https://api.github.com/repos/test/repo/pulls/{pr_number}/commits",
            'review_comments_url': f"https://api.github.com/repos/test/repo/pulls/{pr_number}/comments"
        })()
        
    async def add_pr_comment(self, pr_number, comment):
        if pr_number in self.prs:
            self.prs[pr_number].setdefault('comments', []).append(comment)
            return {"id": len(self.prs[pr_number]['comments'])}
        
    async def is_pr_ready_to_merge(self, pr_number):
        if pr_number in self.prs:
            return {
                "ready": True,
                "reason": "All checks passed",
                "pr_info": self.prs[pr_number]
            }
        return {"ready": False, "reason": "PR not found"}
    
    async def merge_pull_request(self, pr_number, **kwargs):
        if pr_number in self.prs:
            self.prs[pr_number]["state"] = "merged"
            self.prs[pr_number]["merged"] = True
            return {"sha": "abc123", "merged": True}
        return {"error": "PR not found"}

# Mock agents for demo
class MockDevAgent:
    def __init__(self):
        self.github_integration = MockGitHubIntegration()
        
    async def generate_code(self, request):
        """Mock code generation"""
        return {
            "module_name": request["module_spec"]["name"],
            "files": [
                {
                    "filename": f"{request['module_spec']['name'].lower()}.py",
                    "content": f"# Generated {request['module_spec']['name']} module\n\ndef hello():\n    return 'Hello from {request['module_spec']['name']}!'\n",
                    "file_type": "source",
                    "language": "python",
                    "size_bytes": 100
                }
            ],
            "total_files": 1,
            "total_lines": 4,
            "validation_results": {"all_files_valid": True}
        }
    
    async def create_pull_request(self, result, request):
        """Mock PR creation"""
        from types import SimpleNamespace
        
        config = SimpleNamespace()
        config.title = f"Add {result['module_name']} module - Auto-generated code"
        config.body = f"## 🤖 Auto-generated: {result['module_name']}\n\nThis pull request was automatically created by the DevAgent."
        config.head_branch = f"feature/{result['module_name'].lower()}-auto-20240101"
        config.base_branch = "main"
        config.labels = ["auto-generated", "dev-agent", "language-python"]
        
        pr_info = await self.github_integration.create_pull_request(config)
        
        return {
            "pr_number": pr_info.number,
            "pr_url": pr_info.url,
            "branch_name": config.head_branch,
            "status": "created"
        }

class MockReviewAgent:
    def __init__(self):
        self.github_integration = MockGitHubIntegration()
        
    async def review_code(self, request):
        """Mock code review"""
        # Simulate test results
        return {
            "review_id": "review-123",
            "project_id": request["project_id"],
            "module_name": request["module_name"],
            "review_status": "passed",
            "feedback": {
                "review_passed": True,
                "issues_found": [],
                "suggestions": ["Add more comprehensive tests", "Consider error handling"],
                "code_quality_score": 85.5,
                "retry_recommended": False
            },
            "cloud_build_result": {
                "build_id": "build-456",
                "status": "success",
                "duration": 45.2,
                "pytest_results": {
                    "total_tests": 3,
                    "passed": 3,
                    "failed": 0,
                    "coverage_percentage": 95.0
                }
            },
            "created_at": datetime.now()
        }
    
    async def add_pr_comment(self, pr_number, review_result):
        """Mock adding PR comment"""
        comment = f"""## 🤖 ReviewAgent Analysis - {review_result['module_name']}

**Review Status:** ✅ PASSED  
**Quality Score:** {review_result['feedback']['code_quality_score']}/100

### 🧪 Test Results
- **Total Tests:** {review_result['cloud_build_result']['pytest_results']['total_tests']}
- **Passed:** {review_result['cloud_build_result']['pytest_results']['passed']} ✅
- **Failed:** {review_result['cloud_build_result']['pytest_results']['failed']} ❌
- **Coverage:** {review_result['cloud_build_result']['pytest_results']['coverage_percentage']}% ✅

### ✅ Ready for Merge
All tests passed and code quality checks are satisfied. This PR is ready for merge.

---
*🤖 This review was performed automatically by ReviewAgent*
"""
        
        await self.github_integration.add_pr_comment(pr_number, comment)
        return True

class MockOrchestrator:
    def __init__(self):
        self.github_integration = MockGitHubIntegration()
        
    async def check_and_merge_pr(self, pr_number):
        """Mock PR merge check and execution"""
        status = await self.github_integration.is_pr_ready_to_merge(pr_number)
        
        if status["ready"]:
            merge_result = await self.github_integration.merge_pull_request(
                pr_number,
                commit_title=f"Auto-merge: PR #{pr_number} - All checks passed",
                commit_message="Automatically merged by orchestrator after all checks passed"
            )
            
            if merge_result.get("merged"):
                return {"success": True, "message": f"✅ PR #{pr_number} merged successfully!"}
            else:
                return {"success": False, "message": f"❌ Failed to merge PR #{pr_number}"}
        else:
            return {"success": False, "message": f"⏳ PR #{pr_number} not ready: {status['reason']}"}

async def demonstrate_night38_workflow():
    """Demonstrate the complete Night 38 auto-commit workflow"""
    
    print("🚀 Night 38 Auto-Commit Workflow Demo")
    print("=" * 50)
    print()
    
    # Initialize agents
    dev_agent = MockDevAgent()
    review_agent = MockReviewAgent()
    orchestrator = MockOrchestrator()
    
    # Step 1: DevAgent generates code and creates PR
    print("📝 Step 1: DevAgent - Code Generation & PR Creation")
    print("-" * 50)
    
    module_request = {
        "project_id": "demo-project",
        "module_spec": {
            "name": "UserService",
            "description": "Service for user management operations",
            "module_type": "service",
            "language": "python",
            "framework": "fastapi",
            "requirements": ["User CRUD operations", "Authentication integration"]
        }
    }
    
    print(f"🔧 Generating code for: {module_request['module_spec']['name']}")
    code_result = await dev_agent.generate_code(module_request)
    print(f"✅ Generated {code_result['total_files']} files ({code_result['total_lines']} lines)")
    
    print("📋 Creating GitHub PR...")
    pr_result = await dev_agent.create_pull_request(code_result, module_request)
    pr_number = pr_result["pr_number"]
    print(f"✅ PR #{pr_number} created: {pr_result['pr_url']}")
    print()
    
    # Step 2: ReviewAgent reviews code and comments on PR
    print("🔍 Step 2: ReviewAgent - Code Review & PR Comments")
    print("-" * 50)
    
    review_request = {
        "project_id": module_request["project_id"],
        "module_name": module_request["module_spec"]["name"],
        "generated_files": code_result["files"]
    }
    
    print("🧪 Running tests and quality checks...")
    review_result = await review_agent.review_code(review_request)
    print(f"✅ Review completed: {review_result['review_status']}")
    print(f"📊 Quality Score: {review_result['feedback']['code_quality_score']}/100")
    print(f"🧪 Tests: {review_result['cloud_build_result']['pytest_results']['passed']}/{review_result['cloud_build_result']['pytest_results']['total_tests']} passed")
    
    print(f"💬 Adding review comment to PR #{pr_number}...")
    comment_result = await review_agent.add_pr_comment(pr_number, review_result)
    print("✅ Review comment added successfully")
    print()
    
    # Step 3: Orchestrator checks status and merges PR
    print("🔄 Step 3: Orchestrator - Auto-Merge")
    print("-" * 50)
    
    print(f"⚖️  Checking if PR #{pr_number} is ready for merge...")
    await asyncio.sleep(1)  # Simulate check delay
    
    merge_result = await orchestrator.check_and_merge_pr(pr_number)
    print(merge_result["message"])
    
    if merge_result["success"]:
        print("🎉 Auto-commit workflow completed successfully!")
        print()
        print("📋 Summary:")
        print("   • Code generated by DevAgent")
        print(f"   • PR #{pr_number} created automatically")
        print(f"   • Tests passed with {review_result['cloud_build_result']['pytest_results']['coverage_percentage']}% coverage")
        print("   • ReviewAgent added comprehensive feedback")
        print("   • PR merged automatically by Orchestrator")
    else:
        print("⏳ PR will be merged when all checks pass")
    
    print()
    print("🏁 Night 38 Demo Complete!")

async def demonstrate_workflow_with_failures():
    """Demonstrate workflow with test failures and retry logic"""
    
    print("\n🔄 Demonstrating Workflow with Failures")
    print("=" * 50)
    
    # Mock a failing review
    class MockFailingReviewAgent(MockReviewAgent):
        async def review_code(self, request):
            return {
                "review_id": "review-456",
                "project_id": request["project_id"],
                "module_name": request["module_name"],
                "review_status": "failed",
                "feedback": {
                    "review_passed": False,
                    "issues_found": [
                        "Test failure in test_user_creation: AssertionError",
                        "Import error: ModuleNotFoundError for 'database'"
                    ],
                    "suggestions": [
                        "Fix assertion logic in user creation test",
                        "Add missing database module import"
                    ],
                    "code_quality_score": 65.0,
                    "retry_recommended": True
                },
                "cloud_build_result": {
                    "build_id": "build-789",
                    "status": "failure",
                    "duration": 32.1,
                    "pytest_results": {
                        "total_tests": 3,
                        "passed": 1,
                        "failed": 2,
                        "coverage_percentage": 45.0
                    }
                },
                "created_at": datetime.now()
            }
    
    dev_agent = MockDevAgent()
    failing_review_agent = MockFailingReviewAgent()
    orchestrator = MockOrchestrator()
    
    # Generate code and create PR
    print("📝 DevAgent generating code...")
    code_result = await dev_agent.generate_code({
        "project_id": "demo-project-2",
        "module_spec": {
            "name": "OrderService",
            "description": "Service for order management",
            "module_type": "service",
            "language": "python"
        }
    })
    
    pr_result = await dev_agent.create_pull_request(code_result, {})
    pr_number = pr_result["pr_number"]
    print(f"✅ PR #{pr_number} created")
    
    # Review fails
    print("🔍 ReviewAgent reviewing code...")
    review_result = await failing_review_agent.review_code({
        "project_id": "demo-project-2",
        "module_name": "OrderService",
        "generated_files": []
    })
    
    print(f"❌ Review failed: {review_result['review_status']}")
    print(f"🚨 Issues found: {len(review_result['feedback']['issues_found'])}")
    
    # Add failing review comment
    await failing_review_agent.add_pr_comment(pr_number, review_result)
    print("💬 Review comment added with issues and suggestions")
    
    # Orchestrator won't merge
    print("🔄 Orchestrator checking merge status...")
    
    # Mock that PR isn't ready due to failing checks
    class MockOrchestratorWithFailures(MockOrchestrator):
        async def check_and_merge_pr(self, pr_number):
            return {"success": False, "message": f"⏳ PR #{pr_number} not ready: Tests failing"}
    
    failing_orchestrator = MockOrchestratorWithFailures()
    merge_result = await failing_orchestrator.check_and_merge_pr(pr_number)
    print(merge_result["message"])
    
    print("\n🔁 In production, this would trigger DevAgent feedback loop:")
    print("   • ReviewAgent sends issues to DevAgent")
    print("   • DevAgent regenerates improved code")
    print("   • Process repeats until tests pass")
    print("   • Orchestrator merges when all checks pass")

if __name__ == "__main__":
    print("🌟 AI SaaS Factory - Night 38 Auto-Commit Workflow")
    print("DevAgent opens PR; ReviewAgent comments; Orchestrator merges on green")
    print()
    
    # Run the main demo
    asyncio.run(demonstrate_night38_workflow())
    
    # Run the failure scenario demo
    asyncio.run(demonstrate_workflow_with_failures())
    
    print("\n✨ Demo completed! Night 38 implementation ready for production.") 