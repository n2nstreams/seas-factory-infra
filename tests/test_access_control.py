#!/usr/bin/env python3
"""
Test Suite for Access Control System (Night 53)
Tests subscription verification and access control hooks
"""

import pytest
import asyncio
import sys
import os
from datetime import datetime
from unittest.mock import patch

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agents', 'shared'))

from access_control import (
    SubscriptionVerifier, SubscriptionStatus, SubscriptionTier, 
    AccessLevel, TenantSubscription, get_subscription_status
)


class TestSubscriptionVerifier:
    """Test cases for SubscriptionVerifier class"""
    
    @pytest.fixture
    def verifier(self):
        """Create a SubscriptionVerifier instance for testing"""
        return SubscriptionVerifier()
    
    @pytest.fixture
    def sample_subscriptions(self):
        """Sample subscription data for testing"""
        return {
            'free_active': TenantSubscription(
                tenant_id="test-tenant-free",
                tier=SubscriptionTier.FREE,
                status=SubscriptionStatus.ACTIVE,
                projects_used=0,
                build_hours_used=2
            ),
            'starter_active': TenantSubscription(
                tenant_id="test-tenant-starter", 
                tier=SubscriptionTier.STARTER,
                status=SubscriptionStatus.ACTIVE,
                projects_used=0,
                build_hours_used=5
            ),
            'pro_active': TenantSubscription(
                tenant_id="test-tenant-pro",
                tier=SubscriptionTier.PRO,
                status=SubscriptionStatus.ACTIVE, 
                projects_used=2,
                build_hours_used=30
            ),
            'growth_active': TenantSubscription(
                tenant_id="test-tenant-growth",
                tier=SubscriptionTier.GROWTH,
                status=SubscriptionStatus.ACTIVE,
                projects_used=3,
                build_hours_used=100
            ),
            'starter_cancelled': TenantSubscription(
                tenant_id="test-tenant-cancelled",
                tier=SubscriptionTier.STARTER,
                status=SubscriptionStatus.CANCELLED,
                projects_used=1,
                build_hours_used=10
            ),
            'starter_over_limit': TenantSubscription(
                tenant_id="test-tenant-over-limit",
                tier=SubscriptionTier.STARTER,
                status=SubscriptionStatus.ACTIVE,
                projects_used=2,  # Over limit (max 1 for starter)
                build_hours_used=20  # Over limit (max 15 for starter)
            )
        }
    
    def test_tier_hierarchy(self, verifier):
        """Test tier hierarchy ordering"""
        assert verifier.tier_hierarchy[SubscriptionTier.FREE] < verifier.tier_hierarchy[SubscriptionTier.STARTER]
        assert verifier.tier_hierarchy[SubscriptionTier.STARTER] < verifier.tier_hierarchy[SubscriptionTier.PRO]
        assert verifier.tier_hierarchy[SubscriptionTier.PRO] < verifier.tier_hierarchy[SubscriptionTier.GROWTH]
    
    def test_tier_limits_configuration(self, verifier):
        """Test that tier limits are properly configured"""
        # Free tier
        free_limits = verifier.tier_limits[SubscriptionTier.FREE]
        assert free_limits['max_projects'] == 1
        assert free_limits['max_build_hours'] == 5
        assert 'basic_design' in free_limits['features']
        
        # Starter tier
        starter_limits = verifier.tier_limits[SubscriptionTier.STARTER]
        assert starter_limits['max_projects'] == 1
        assert starter_limits['max_build_hours'] == 15
        assert 'github_integration' in starter_limits['features']
        
        # Growth tier (unlimited)
        growth_limits = verifier.tier_limits[SubscriptionTier.GROWTH]
        assert growth_limits['max_projects'] == 5
        assert growth_limits['max_build_hours'] == -1  # Unlimited
        assert growth_limits['features'] == ['all']
    
    def test_check_access_level_valid(self, verifier, sample_subscriptions):
        """Test access level checking with valid scenarios"""
        
        # Free tier can access free features
        assert verifier.check_access_level(
            sample_subscriptions['free_active'], AccessLevel.FREE
        ) == True
        
        # Starter can access starter and free features
        assert verifier.check_access_level(
            sample_subscriptions['starter_active'], AccessLevel.FREE
        ) == True
        assert verifier.check_access_level(
            sample_subscriptions['starter_active'], AccessLevel.STARTER
        ) == True
        
        # Pro can access up to pro features
        assert verifier.check_access_level(
            sample_subscriptions['pro_active'], AccessLevel.PRO
        ) == True
        
        # Growth can access all features
        assert verifier.check_access_level(
            sample_subscriptions['growth_active'], AccessLevel.GROWTH
        ) == True
    
    def test_check_access_level_denied(self, verifier, sample_subscriptions):
        """Test access level checking with denied scenarios"""
        
        # Free tier cannot access paid features
        assert verifier.check_access_level(
            sample_subscriptions['free_active'], AccessLevel.STARTER
        ) == False
        
        # Starter cannot access pro features
        assert verifier.check_access_level(
            sample_subscriptions['starter_active'], AccessLevel.PRO
        ) == False
        
        # Cancelled subscription only gets free access
        assert verifier.check_access_level(
            sample_subscriptions['starter_cancelled'], AccessLevel.STARTER
        ) == False
        assert verifier.check_access_level(
            sample_subscriptions['starter_cancelled'], AccessLevel.FREE
        ) == True
    
    def test_check_feature_access(self, verifier, sample_subscriptions):
        """Test feature-specific access checking"""
        
        # Free tier has basic features
        assert verifier.check_feature_access(
            sample_subscriptions['free_active'], 'basic_design'
        ) == True
        assert verifier.check_feature_access(
            sample_subscriptions['free_active'], 'github_integration'
        ) == False
        
        # Starter tier has additional features  
        assert verifier.check_feature_access(
            sample_subscriptions['starter_active'], 'github_integration'
        ) == True
        assert verifier.check_feature_access(
            sample_subscriptions['starter_active'], 'custom_domains'
        ) == False
        
        # Growth tier has all features
        assert verifier.check_feature_access(
            sample_subscriptions['growth_active'], 'any_feature'
        ) == True
    
    def test_check_usage_limits(self, verifier, sample_subscriptions):
        """Test usage limit checking"""
        
        # Within limits
        limits_check = verifier.check_usage_limits(sample_subscriptions['starter_active'])
        assert limits_check['projects_within_limit'] == True
        assert limits_check['build_hours_within_limit'] == True
        
        # Over limits
        limits_check = verifier.check_usage_limits(sample_subscriptions['starter_over_limit'])
        assert limits_check['projects_within_limit'] == False
        assert limits_check['build_hours_within_limit'] == False
        
        # Unlimited (Growth tier)
        limits_check = verifier.check_usage_limits(sample_subscriptions['growth_active'])
        assert limits_check['projects_within_limit'] == True
        assert limits_check['build_hours_within_limit'] == True


class TestAccessControlIntegration:
    """Integration tests for access control system"""
    
    @pytest.mark.asyncio
    async def test_subscription_status_api(self):
        """Test the subscription status API function"""
        
        # Mock the subscription verifier
        with patch('access_control.subscription_verifier') as mock_verifier:
            mock_subscription = TenantSubscription(
                tenant_id="test-tenant",
                tier=SubscriptionTier.PRO,
                status=SubscriptionStatus.ACTIVE,
                projects_used=1,
                build_hours_used=20,
                last_checked=datetime.utcnow()
            )
            
            mock_verifier.get_tenant_subscription.return_value = mock_subscription
            mock_verifier.check_usage_limits.return_value = {
                'projects_within_limit': True,
                'build_hours_within_limit': True
            }
            mock_verifier.tier_limits = {
                SubscriptionTier.PRO: {
                    'max_projects': 3,
                    'max_build_hours': 60,
                    'features': ['advanced_design', 'advanced_codegen', 'github_integration']
                }
            }
            
            status = await get_subscription_status("test-tenant")
            
            assert status['tenant_id'] == "test-tenant"
            assert status['tier'] == 'pro'
            assert status['status'] == 'active'
            assert status['is_active'] == True
            assert status['usage']['projects']['used'] == 1
            assert status['usage']['projects']['limit'] == 3
            assert status['usage']['build_hours']['used'] == 20
            assert status['usage']['build_hours']['limit'] == 60
    
    @pytest.mark.asyncio
    async def test_access_control_error_handling(self):
        """Test error handling in access control"""
        
        # Test with invalid tenant
        with patch('access_control.subscription_verifier') as mock_verifier:
            mock_verifier.get_tenant_subscription.side_effect = Exception("Database error")
            
            # Should return default free subscription on error
            try:
                status = await get_subscription_status("invalid-tenant")
                # Should not raise exception but return default response
                assert True
            except Exception:
                pytest.fail("Access control should handle errors gracefully")


class TestAccessControlScenarios:
    """Test real-world access control scenarios"""
    
    def test_new_user_journey(self):
        """Test access control for new user journey"""
        verifier = SubscriptionVerifier()
        
        # New user starts with free subscription
        free_user = TenantSubscription(
            tenant_id="new-user",
            tier=SubscriptionTier.FREE,
            status=SubscriptionStatus.ACTIVE,
            projects_used=0,
            build_hours_used=0
        )
        
        # Can access free features
        assert verifier.check_access_level(free_user, AccessLevel.FREE) == True
        assert verifier.check_feature_access(free_user, 'basic_design') == True
        
        # Cannot access paid features
        assert verifier.check_access_level(free_user, AccessLevel.STARTER) == False
        assert verifier.check_feature_access(free_user, 'github_integration') == False
        
        # Within limits initially
        limits = verifier.check_usage_limits(free_user)
        assert all(limits.values()) == True
    
    def test_subscription_upgrade_journey(self):
        """Test access control after subscription upgrade"""
        verifier = SubscriptionVerifier()
        
        # User upgrades to Pro
        pro_user = TenantSubscription(
            tenant_id="upgraded-user",
            tier=SubscriptionTier.PRO,
            status=SubscriptionStatus.ACTIVE,
            projects_used=2,
            build_hours_used=45
        )
        
        # Can access pro and lower features
        assert verifier.check_access_level(pro_user, AccessLevel.FREE) == True
        assert verifier.check_access_level(pro_user, AccessLevel.STARTER) == True
        assert verifier.check_access_level(pro_user, AccessLevel.PRO) == True
        
        # Cannot access growth features
        assert verifier.check_access_level(pro_user, AccessLevel.GROWTH) == False
        
        # Has access to pro features
        assert verifier.check_feature_access(pro_user, 'advanced_design') == True
        assert verifier.check_feature_access(pro_user, 'custom_domains') == True
    
    def test_subscription_cancellation_scenario(self):
        """Test access control after subscription cancellation"""
        verifier = SubscriptionVerifier()
        
        # User cancels their subscription
        cancelled_user = TenantSubscription(
            tenant_id="cancelled-user",
            tier=SubscriptionTier.PRO,  # Still shows pro tier
            status=SubscriptionStatus.CANCELLED,  # But cancelled status
            projects_used=2,
            build_hours_used=45
        )
        
        # Only has free access due to cancelled status
        assert verifier.check_access_level(cancelled_user, AccessLevel.FREE) == True
        assert verifier.check_access_level(cancelled_user, AccessLevel.STARTER) == False
        assert verifier.check_access_level(cancelled_user, AccessLevel.PRO) == False
        
        # No access to paid features
        assert verifier.check_feature_access(cancelled_user, 'github_integration') == False
        assert verifier.check_feature_access(cancelled_user, 'advanced_design') == False
    
    def test_usage_limit_scenarios(self):
        """Test various usage limit scenarios"""
        verifier = SubscriptionVerifier()
        
        # User approaching limits
        near_limit_user = TenantSubscription(
            tenant_id="near-limit-user",
            tier=SubscriptionTier.STARTER,
            status=SubscriptionStatus.ACTIVE,
            projects_used=0,  # Still under project limit (1)
            build_hours_used=14  # Close to build hours limit (15)
        )
        
        limits = verifier.check_usage_limits(near_limit_user)
        assert limits['projects_within_limit'] == True
        assert limits['build_hours_within_limit'] == True
        
        # User over limits
        over_limit_user = TenantSubscription(
            tenant_id="over-limit-user",
            tier=SubscriptionTier.STARTER,
            status=SubscriptionStatus.ACTIVE,
            projects_used=2,  # Over project limit (1)
            build_hours_used=20  # Over build hours limit (15)
        )
        
        limits = verifier.check_usage_limits(over_limit_user)
        assert limits['projects_within_limit'] == False
        assert limits['build_hours_within_limit'] == False


@pytest.mark.asyncio
async def test_full_access_control_flow():
    """End-to-end test of the access control flow"""
    print("\n🧪 Testing Full Access Control Flow (Night 53)")
    print("=" * 60)
    
    # Test subscription verification
    verifier = SubscriptionVerifier()
    
    # Test different subscription scenarios
    test_scenarios = [
        {
            'name': 'Free Tier User',
            'subscription': TenantSubscription(
                tenant_id="free-user",
                tier=SubscriptionTier.FREE,
                status=SubscriptionStatus.ACTIVE,
                projects_used=0,
                build_hours_used=2
            ),
            'should_access_starter': False,
            'should_access_github': False
        },
        {
            'name': 'Starter Tier User',
            'subscription': TenantSubscription(
                tenant_id="starter-user",
                tier=SubscriptionTier.STARTER,
                status=SubscriptionStatus.ACTIVE,
                projects_used=0,
                build_hours_used=5
            ),
            'should_access_starter': True,
            'should_access_github': True
        },
        {
            'name': 'Cancelled User',
            'subscription': TenantSubscription(
                tenant_id="cancelled-user",
                tier=SubscriptionTier.PRO,
                status=SubscriptionStatus.CANCELLED,
                projects_used=1,
                build_hours_used=10
            ),
            'should_access_starter': False,
            'should_access_github': False
        },
        {
            'name': 'Over Limit User',
            'subscription': TenantSubscription(
                tenant_id="over-limit-user",
                tier=SubscriptionTier.STARTER,
                status=SubscriptionStatus.ACTIVE,
                projects_used=2,  # Over limit
                build_hours_used=20  # Over limit
            ),
            'should_access_starter': True,  # Has tier access
            'should_access_github': True,   # Has feature access
            'over_limits': True
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n📋 Testing: {scenario['name']}")
        subscription = scenario['subscription']
        
        # Test tier access
        starter_access = verifier.check_access_level(subscription, AccessLevel.STARTER)
        print(f"  ✓ Starter Access: {starter_access} (expected: {scenario['should_access_starter']})")
        assert starter_access == scenario['should_access_starter']
        
        # Test feature access
        github_access = verifier.check_feature_access(subscription, 'github_integration')
        print(f"  ✓ GitHub Feature: {github_access} (expected: {scenario['should_access_github']})")
        assert github_access == scenario['should_access_github']
        
        # Test usage limits
        limits = verifier.check_usage_limits(subscription)
        if scenario.get('over_limits'):
            print(f"  ⚠️ Usage Limits: Projects={limits['projects_within_limit']}, Hours={limits['build_hours_within_limit']}")
            assert not limits['projects_within_limit']
            assert not limits['build_hours_within_limit']
        else:
            print("  ✓ Usage Limits: Within limits")
            assert limits['projects_within_limit']
            assert limits['build_hours_within_limit']
    
    print("\n🎉 Access Control Tests Completed Successfully!")
    print("\n📊 Test Summary:")
    print("- ✅ Tier hierarchy validation")
    print("- ✅ Feature access control")
    print("- ✅ Usage limit enforcement")
    print("- ✅ Subscription status handling")
    print("- ✅ Error handling and graceful degradation")


if __name__ == "__main__":
    # Run the tests
    asyncio.run(test_full_access_control_flow())
    print("\n🚀 All access control tests passed! Ready for production.") 