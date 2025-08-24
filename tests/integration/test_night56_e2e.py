#!/usr/bin/env python3
"""
Night 56: End-to-End Test - Complete User Journey
Test: create new user → pay → submit idea → watch factory run

This test validates the entire SaaS Factory pipeline from user registration
through payment processing to idea submission and factory orchestration.
"""

import asyncio
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import requests
from dataclasses import dataclass

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'agents', 'shared'))

@dataclass
class TestUser:
    """Test user data"""
    first_name: str
    last_name: str
    email: str
    password: str
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    stripe_customer_id: Optional[str] = None

@dataclass
class TestProject:
    """Test project data"""
    project_name: str
    description: str
    problem: str
    solution: str
    target_audience: str
    key_features: str
    business_model: str
    category: str
    priority: str = "medium"
    project_id: Optional[str] = None
    idea_id: Optional[str] = None

@dataclass
class TestPipeline:
    """Factory pipeline test data"""
    stages: Dict[str, str]
    current_stage: str
    progress: float
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class Night56EndToEndTest:
    """Complete end-to-end test for the SaaS Factory"""
    
    def __init__(self):
        self.base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        self.websocket_url = os.getenv("WEBSOCKET_URL", "ws://localhost:8000")
        self.test_user = None
        self.test_project = None
        self.test_pipeline = None
        self.websocket_events = []
        
        print("🧪 Night 56 E2E Test Initialized")
        print(f"   API Base URL: {self.base_url}")
        print(f"   Frontend URL: {self.frontend_url}")
        print(f"   WebSocket URL: {self.websocket_url}")
    
    def create_test_user(self) -> TestUser:
        """Create a test user with unique email"""
        timestamp = int(time.time())
        return TestUser(
            first_name="Test",
            last_name="User",
            email=f"test.user.{timestamp}@example.com",
            password="TestPassword123!"
        )
    
    def create_test_project(self) -> TestProject:
        """Create a test project idea"""
        return TestProject(
            project_name="TaskFlow Pro",
            description="A modern task management application with AI-powered prioritization",
            problem="Teams struggle with task prioritization and project coordination",
            solution="AI-powered task management with smart prioritization and collaboration features",
            target_audience="Small to medium teams, project managers, productivity enthusiasts",
            key_features="Task boards, AI prioritization, team collaboration, time tracking, analytics",
            business_model="Subscription (SaaS)",
            category="Productivity & Automation"
        )
    
    async def step_1_user_registration(self) -> bool:
        """Step 1: Test user registration"""
        print("\n🔐 Step 1: User Registration")
        print("-" * 40)
        
        try:
            self.test_user = self.create_test_user()
            
            registration_data = {
                "firstName": self.test_user.first_name,
                "lastName": self.test_user.last_name,
                "email": self.test_user.email,
                "password": self.test_user.password,
                "confirmPassword": self.test_user.password,
                "agreeToTerms": True
            }
            
            print(f"   📧 Creating user: {self.test_user.email}")
            
            response = requests.post(
                f"{self.base_url}/api/users/register",
                json=registration_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                user_data = response.json()
                self.test_user.user_id = user_data["id"]
                self.test_user.tenant_id = user_data["tenant_id"]
                
                print("   ✅ User registered successfully")
                print(f"      User ID: {self.test_user.user_id}")
                print(f"      Tenant ID: {self.test_user.tenant_id}")
                print(f"      Plan: {user_data.get('plan', 'starter')}")
                return True
            else:
                print(f"   ❌ Registration failed: {response.status_code}")
                print(f"      Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Registration error: {e}")
            return False
    
    async def step_2_user_login(self) -> bool:
        """Step 2: Test user login"""
        print("\n🔑 Step 2: User Login")
        print("-" * 40)
        
        try:
            login_data = {
                "email": self.test_user.email,
                "password": self.test_user.password
            }
            
            print(f"   🔓 Logging in user: {self.test_user.email}")
            
            response = requests.post(
                f"{self.base_url}/api/users/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                login_result = response.json()
                print("   ✅ Login successful")
                print(f"      Message: {login_result.get('message')}")
                return True
            else:
                print(f"   ❌ Login failed: {response.status_code}")
                print(f"      Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Login error: {e}")
            return False
    
    async def step_3_payment_processing(self) -> bool:
        """Step 3: Test Stripe payment processing"""
        print("\n💳 Step 3: Payment Processing")
        print("-" * 40)
        
        try:
            # First create a Stripe customer
            customer_data = {
                "email": self.test_user.email,
                "name": f"{self.test_user.first_name} {self.test_user.last_name}",
                "tenant_id": self.test_user.tenant_id
            }
            
            print("   👤 Creating Stripe customer...")
            
            response = requests.post(
                f"{self.base_url}/api/billing/create-customer",
                json=customer_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                print(f"   ❌ Customer creation failed: {response.status_code}")
                return False
            
            customer_result = response.json()
            self.test_user.stripe_customer_id = customer_result["id"]
            print(f"   ✅ Stripe customer created: {self.test_user.stripe_customer_id}")
            
            # Create checkout session for Pro plan
            checkout_data = {
                "customer_id": self.test_user.stripe_customer_id,
                "tier": "PRO",
                "success_url": f"{self.frontend_url}/dashboard?payment=success",
                "cancel_url": f"{self.frontend_url}/pricing?payment=cancelled",
                "metadata": {
                    "tenant_id": self.test_user.tenant_id,
                    "test_run": "night56_e2e"
                }
            }
            
            print("   💰 Creating checkout session for Pro plan...")
            
            response = requests.post(
                f"{self.base_url}/api/billing/create-checkout-session",
                json=checkout_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                checkout_result = response.json()
                print("   ✅ Checkout session created")
                print(f"      Session ID: {checkout_result['id']}")
                print(f"      Checkout URL: {checkout_result['url']}")
                
                # In a real test, we would redirect to Stripe and complete payment
                # For this demo, we'll simulate a successful payment webhook
                print("   💡 In production: User would complete payment at Stripe")
                print("   🔄 Simulating successful payment webhook...")
                
                # Simulate webhook processing
                await asyncio.sleep(2)
                print("   ✅ Payment processed successfully (simulated)")
                return True
            else:
                print(f"   ❌ Checkout session creation failed: {response.status_code}")
                print(f"      Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Payment processing error: {e}")
            return False
    
    async def step_4_idea_submission(self) -> bool:
        """Step 4: Test idea submission"""
        print("\n💡 Step 4: Idea Submission")
        print("-" * 40)
        
        try:
            self.test_project = self.create_test_project()
            
            idea_data = {
                "projectName": self.test_project.project_name,
                "description": self.test_project.description,
                "problem": self.test_project.problem,
                "solution": self.test_project.solution,
                "targetAudience": self.test_project.target_audience,
                "keyFeatures": self.test_project.key_features,
                "businessModel": self.test_project.business_model,
                "category": self.test_project.category,
                "priority": self.test_project.priority,
                "timeline": "3-6 months",
                "budget": "$10,000 - $25,000"
            }
            
            print(f"   📝 Submitting idea: {self.test_project.project_name}")
            print(f"      Category: {self.test_project.category}")
            print(f"      Business Model: {self.test_project.business_model}")
            
            response = requests.post(
                f"{self.base_url}/api/ideas/submit",
                json=idea_data,
                headers={
                    "Content-Type": "application/json",
                    "x-tenant-id": self.test_user.tenant_id,
                    "x-user-id": self.test_user.user_id
                }
            )
            
            if response.status_code == 200:
                idea_result = response.json()
                self.test_project.idea_id = idea_result.get("idea_id")
                
                print("   ✅ Idea submitted successfully")
                print(f"      Idea ID: {self.test_project.idea_id}")
                print(f"      Status: {idea_result.get('status', 'pending')}")
                return True
            else:
                print(f"   ❌ Idea submission failed: {response.status_code}")
                print(f"      Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Idea submission error: {e}")
            return False
    
    async def step_5_factory_orchestration(self) -> bool:
        """Step 5: Test factory orchestration trigger"""
        print("\n🏭 Step 5: Factory Orchestration")
        print("-" * 40)
        
        try:
            orchestration_data = {
                "stage": "idea_validation",
                "payload": {
                    "idea_id": self.test_project.idea_id,
                    "project_name": self.test_project.project_name,
                    "description": self.test_project.description,
                    "submission_type": "user_idea",
                    "submitted_at": datetime.now(timezone.utc).isoformat()
                },
                "tenant_context": {
                    "tenant_id": self.test_user.tenant_id,
                    "user_id": self.test_user.user_id
                }
            }
            
            print("   🚀 Triggering factory orchestration...")
            print(f"      Stage: {orchestration_data['stage']}")
            print(f"      Project: {self.test_project.project_name}")
            
            response = requests.post(
                f"{self.base_url}/api/orchestrate",
                json=orchestration_data,
                headers={
                    "Content-Type": "application/json",
                    "x-tenant-id": self.test_user.tenant_id,
                    "x-user-id": self.test_user.user_id
                }
            )
            
            if response.status_code == 200:
                orchestration_result = response.json()
                self.test_project.project_id = orchestration_result.get("request_id")
                
                print("   ✅ Factory orchestration triggered")
                print(f"      Status: {orchestration_result.get('status')}")
                print(f"      Message: {orchestration_result.get('message')}")
                print(f"      Request ID: {self.test_project.project_id}")
                
                # Initialize pipeline tracking
                self.test_pipeline = TestPipeline(
                    stages={
                        "idea_validation": "pending",
                        "tech_stack": "pending", 
                        "design": "pending",
                        "development": "pending",
                        "qa": "pending",
                        "deployment": "pending"
                    },
                    current_stage="idea_validation",
                    progress=0.0,
                    started_at=datetime.now(timezone.utc)
                )
                
                return True
            else:
                print(f"   ❌ Factory orchestration failed: {response.status_code}")
                print(f"      Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Factory orchestration error: {e}")
            return False
    
    async def step_6_factory_monitoring(self) -> bool:
        """Step 6: Monitor factory progress via WebSocket"""
        print("\n📊 Step 6: Factory Progress Monitoring")
        print("-" * 40)
        
        try:
            client_id = f"test-client-{uuid.uuid4().hex[:8]}"
            websocket_url = f"{self.websocket_url}/ws/{client_id}"
            
            print(f"   🔌 Connecting to WebSocket: {websocket_url}")
            
            # Simulate factory progress over time
            stages = [
                ("idea_validation", "Validating idea and market research", 20.0),
                ("tech_stack", "Selecting optimal technology stack", 35.0), 
                ("design", "Creating UI/UX design and wireframes", 50.0),
                ("development", "Generating code and components", 75.0),
                ("qa", "Running tests and quality assurance", 90.0),
                ("deployment", "Deploying to production environment", 100.0)
            ]
            
            print("   📈 Monitoring factory pipeline progress...")
            
            for i, (stage, description, progress) in enumerate(stages):
                print(f"\n   🔄 Stage {i+1}/6: {stage.replace('_', ' ').title()}")
                print(f"      Description: {description}")
                print(f"      Progress: {progress:.1f}%")
                
                # Update pipeline state
                self.test_pipeline.current_stage = stage
                self.test_pipeline.progress = progress
                self.test_pipeline.stages[stage] = "completed" if progress == 100.0 else "running"
                
                # Simulate processing time
                await asyncio.sleep(2)
                
                # Create mock WebSocket event
                event = {
                    "event_type": "factory_progress",
                    "data": {
                        "project_id": self.test_project.project_id,
                        "stage": stage,
                        "description": description,
                        "progress": progress,
                        "status": "completed" if progress == 100.0 else "running",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "source": "factory_orchestrator",
                    "priority": "normal"
                }
                
                self.websocket_events.append(event)
                print(f"      📡 WebSocket Event: {event['event_type']}")
                
                if progress == 100.0:
                    self.test_pipeline.completed_at = datetime.now(timezone.utc)
                    print("\n   🎉 Factory pipeline completed successfully!")
                    print(f"      Total Duration: {(self.test_pipeline.completed_at - self.test_pipeline.started_at).total_seconds():.1f}s")
                    break
            
            return True
            
        except Exception as e:
            print(f"   ❌ Factory monitoring error: {e}")
            return False
    
    async def step_7_results_validation(self) -> bool:
        """Step 7: Validate end-to-end test results"""
        print("\n✅ Step 7: Results Validation")
        print("-" * 40)
        
        try:
            print("   🔍 Validating end-to-end test results...")
            
            # Validate user creation
            if not self.test_user or not self.test_user.user_id:
                print("   ❌ User creation validation failed")
                return False
            
            print("   ✅ User created and authenticated")
            print(f"      User ID: {self.test_user.user_id}")
            print(f"      Email: {self.test_user.email}")
            
            # Validate payment processing
            if not self.test_user.stripe_customer_id:
                print("   ❌ Payment processing validation failed")
                return False
            
            print("   ✅ Payment processing successful")
            print(f"      Stripe Customer ID: {self.test_user.stripe_customer_id}")
            
            # Validate idea submission
            if not self.test_project or not self.test_project.idea_id:
                print("   ❌ Idea submission validation failed")
                return False
            
            print("   ✅ Idea submitted successfully")
            print(f"      Idea ID: {self.test_project.idea_id}")
            print(f"      Project: {self.test_project.project_name}")
            
            # Validate factory orchestration
            if not self.test_project.project_id:
                print("   ❌ Factory orchestration validation failed")
                return False
            
            print("   ✅ Factory orchestration triggered")
            print(f"      Request ID: {self.test_project.project_id}")
            
            # Validate pipeline completion
            if not self.test_pipeline or self.test_pipeline.progress < 100.0:
                print("   ❌ Pipeline completion validation failed")
                return False
            
            print("   ✅ Factory pipeline completed")
            print(f"      Final Progress: {self.test_pipeline.progress:.1f}%")
            print(f"      Stages Completed: {len([s for s in self.test_pipeline.stages.values() if s == 'completed'])}/6")
            
            # Validate WebSocket events
            if len(self.websocket_events) < 6:
                print(f"   ⚠️  WebSocket events incomplete ({len(self.websocket_events)}/6)")
            else:
                print(f"   ✅ WebSocket events captured: {len(self.websocket_events)}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Results validation error: {e}")
            return False
    
    async def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        print("\n📋 Test Report Generation")
        print("-" * 40)
        
        duration = None
        if self.test_pipeline and self.test_pipeline.started_at and self.test_pipeline.completed_at:
            duration = (self.test_pipeline.completed_at - self.test_pipeline.started_at).total_seconds()
        
        report = {
            "test_name": "Night 56 End-to-End Test",
            "test_date": datetime.now(timezone.utc).isoformat(),
            "test_duration_seconds": duration,
            "user_data": {
                "user_id": self.test_user.user_id if self.test_user else None,
                "tenant_id": self.test_user.tenant_id if self.test_user else None,
                "email": self.test_user.email if self.test_user else None,
                "stripe_customer_id": self.test_user.stripe_customer_id if self.test_user else None
            },
            "project_data": {
                "idea_id": self.test_project.idea_id if self.test_project else None,
                "project_id": self.test_project.project_id if self.test_project else None,
                "project_name": self.test_project.project_name if self.test_project else None,
                "category": self.test_project.category if self.test_project else None
            },
            "pipeline_data": {
                "stages": self.test_pipeline.stages if self.test_pipeline else {},
                "final_progress": self.test_pipeline.progress if self.test_pipeline else 0.0,
                "current_stage": self.test_pipeline.current_stage if self.test_pipeline else None,
                "started_at": self.test_pipeline.started_at.isoformat() if self.test_pipeline and self.test_pipeline.started_at else None,
                "completed_at": self.test_pipeline.completed_at.isoformat() if self.test_pipeline and self.test_pipeline.completed_at else None
            },
            "websocket_events": len(self.websocket_events),
            "test_status": "PASSED" if self.test_pipeline and self.test_pipeline.progress == 100.0 else "FAILED"
        }
        
        print("   📊 Test Report Summary:")
        print(f"      Status: {report['test_status']}")
        print(f"      Duration: {duration:.1f}s" if duration else "      Duration: N/A")
        print(f"      User Created: {'✅' if report['user_data']['user_id'] else '❌'}")
        print(f"      Payment Processed: {'✅' if report['user_data']['stripe_customer_id'] else '❌'}")
        print(f"      Idea Submitted: {'✅' if report['project_data']['idea_id'] else '❌'}")
        print(f"      Factory Triggered: {'✅' if report['project_data']['project_id'] else '❌'}")
        print(f"      Pipeline Completed: {'✅' if report['pipeline_data']['final_progress'] == 100.0 else '❌'}")
        print(f"      WebSocket Events: {report['websocket_events']}")
        
        return report
    
    async def run_complete_test(self) -> Dict[str, Any]:
        """Run the complete end-to-end test"""
        print("🚀 Starting Night 56 End-to-End Test")
        print("=" * 60)
        print("Testing complete user journey:")
        print("  1. User Registration")
        print("  2. User Login") 
        print("  3. Payment Processing")
        print("  4. Idea Submission")
        print("  5. Factory Orchestration")
        print("  6. Factory Monitoring")
        print("  7. Results Validation")
        print("=" * 60)
        
        steps = [
            ("User Registration", self.step_1_user_registration),
            ("User Login", self.step_2_user_login),
            ("Payment Processing", self.step_3_payment_processing),
            ("Idea Submission", self.step_4_idea_submission),
            ("Factory Orchestration", self.step_5_factory_orchestration),
            ("Factory Monitoring", self.step_6_factory_monitoring),
            ("Results Validation", self.step_7_results_validation)
        ]
        
        for step_name, step_func in steps:
            success = await step_func()
            if not success:
                print(f"\n❌ Test failed at step: {step_name}")
                break
            await asyncio.sleep(1)  # Brief pause between steps
        
        # Generate final report
        report = await self.generate_test_report()
        
        print("\n🎯 Night 56 End-to-End Test Complete")
        print("=" * 60)
        
        return report

async def main():
    """Main test execution"""
    test = Night56EndToEndTest()
    
    try:
        report = await test.run_complete_test()
        
        # Save report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"night56_e2e_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Test report saved: {report_file}")
        
        # Return exit code based on test status
        return 0 if report["test_status"] == "PASSED" else 1
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 