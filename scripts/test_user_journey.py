#!/usr/bin/env python3
"""
User Journey Testing Script for SaaS Factory Audit Fixes
Tests the complete user journey from signup to idea submission
"""

import asyncio
import aiohttp
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserJourneyTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.user_data = None
        self.auth_headers = {}

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def test_account_creation(self) -> bool:
        """Test account creation flow"""
        try:
            # Test user data
            user_data = {
                "firstName": "Test",
                "lastName": "User",
                "email": f"test_{int(asyncio.get_event_loop().time())}@example.com",
                "password": "TestPassword123!",
                "confirmPassword": "TestPassword123!",
                "agreeToTerms": True
            }

            logger.info("Testing account creation...")
            async with self.session.post(
                f"{self.base_url}/api/users/register",
                json=user_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self.user_data = result
                    self.auth_headers = {
                        "X-Tenant-ID": result["tenant_id"],
                        "X-User-ID": result["id"]
                    }
                    logger.info(f"✅ Account creation successful: {result['email']}")
                    return True
                elif response.status == 409:
                    logger.warning("⚠️  Email already exists, trying login instead")
                    return await self.test_login(user_data["email"], user_data["password"])
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Account creation failed: {response.status} - {error_text}")
                    return False

        except Exception as e:
            logger.error(f"❌ Account creation error: {e}")
            return False

    async def test_login(self, email: str, password: str) -> bool:
        """Test login flow"""
        try:
            login_data = {
                "email": email,
                "password": password
            }

            logger.info("Testing login...")
            async with self.session.post(
                f"{self.base_url}/api/users/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self.user_data = result["user"]
                    self.auth_headers = {
                        "X-Tenant-ID": result["user"]["tenant_id"],
                        "X-User-ID": result["user"]["id"]
                    }
                    logger.info(f"✅ Login successful: {result['user']['email']}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Login failed: {response.status} - {error_text}")
                    return False

        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return False

    async def test_idea_submission(self) -> bool:
        """Test idea submission flow"""
        try:
            # Test idea data
            idea_data = {
                "title": "AI Task Management Tool",
                "description": "An intelligent task management system that uses AI to prioritize and organize tasks",
                "category": "Productivity & Automation",
                "problem": "People struggle to prioritize tasks effectively and manage their time",
                "solution": "AI-powered task management with smart prioritization and time blocking",
                "targetAudience": "Freelancers and small business owners",
                "keyFeatures": "Smart task prioritization, Time blocking, AI suggestions",
                "businessModel": "Subscription (SaaS)",
                "timeline": "2-3 months",
                "budget_range": "$5,000 - $10,000"
            }

            logger.info("Testing idea submission...")
            async with self.session.post(
                f"{self.base_url}/api/ideas/submit",
                json=idea_data,
                headers={**self.auth_headers, "Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Idea submission successful: {result['title']}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Idea submission failed: {response.status} - {error_text}")
                    return False

        except Exception as e:
            logger.error(f"❌ Idea submission error: {e}")
            return False

    async def test_session_consistency(self) -> bool:
        """Test session consistency across requests"""
        try:
            logger.info("Testing session consistency...")

            # Test profile endpoint
            async with self.session.get(
                f"{self.base_url}/api/users/profile",
                headers=self.auth_headers
            ) as response:
                if response.status != 200:
                    logger.error(f"❌ Profile endpoint failed: {response.status}")
                    return False

            # Test ideas endpoint
            async with self.session.get(
                f"{self.base_url}/api/ideas/my-ideas",
                headers=self.auth_headers
            ) as response:
                if response.status not in [200, 404]:  # 404 is OK if no ideas yet
                    logger.error(f"❌ My ideas endpoint failed: {response.status}")
                    return False

            logger.info("✅ Session consistency test passed")
            return True

        except Exception as e:
            logger.error(f"❌ Session consistency error: {e}")
            return False

    async def run_complete_journey(self) -> bool:
        """Run the complete user journey test"""
        logger.info("🚀 Starting User Journey Test")
        logger.info("=" * 50)

        tests = [
            ("Account Creation/Login", self.test_account_creation),
            ("Session Consistency", self.test_session_consistency),
            ("Idea Submission", self.test_idea_submission),
        ]

        results = []
        for test_name, test_func in tests:
            logger.info(f"\n📋 Running {test_name}...")
            result = await test_func()
            results.append((test_name, result))

            if not result:
                logger.error(f"❌ {test_name} failed - stopping journey")
                break

        # Summary
        logger.info("\n" + "=" * 50)
        logger.info("📊 Test Results Summary:")

        all_passed = True
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"  {test_name}: {status}")
            if not result:
                all_passed = False

        if all_passed:
            logger.info("\n🎉 All tests passed! User journey is working correctly.")
        else:
            logger.error("\n💥 Some tests failed. User journey needs attention.")

        return all_passed

async def main():
    """Main test runner"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"

    logger.info(f"Testing against: {base_url}")

    async with UserJourneyTester(base_url) as tester:
        success = await tester.run_complete_journey()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
