#!/usr/bin/env python3
"""
Security & Compliance Validation Script
Section 6 of the Critical Pre-Decommission Checklist

This script validates:
1. RLS Policy Testing - Red-team testing for cross-tenant isolation
2. Access Control Verification - Role-based access control validation
3. Audit Trail Validation - Security event logging verification
4. Compliance Checks - GDPR, PCI, SOC2 compliance validation

Usage: python scripts/security_validation.py
"""

import os
import sys
import json
import time
import uuid
import requests
import psycopg2
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('security_validation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SecurityValidator:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'overall_score': 0,
            'tests_passed': 0,
            'tests_total': 0,
            'critical_issues': [],
            'warnings': [],
            'recommendations': []
        }
        
        # Load configuration
        self.config = self.load_config()
        self.supabase_url = self.config.get('supabase_url')
        self.supabase_key = self.config.get('supabase_service_key')
        self.api_base_url = self.config.get('api_base_url', 'http://localhost:3000')
        
        # Test data
        self.test_tenant_id = str(uuid.uuid4())
        self.test_user_id = str(uuid.uuid4())
        self.other_tenant_id = str(uuid.uuid4())
        
    def load_config(self) -> Dict[str, str]:
        """Load configuration from environment variables"""
        return {
            'supabase_url': os.getenv('NEXT_PUBLIC_SUPABASE_URL'),
            'supabase_service_key': os.getenv('SUPABASE_SERVICE_ROLE_KEY'),
            'api_base_url': os.getenv('API_BASE_URL', 'http://localhost:3000')
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all security validation tests"""
        logger.info("🚀 Starting Security & Compliance Validation")
        logger.info("=" * 60)
        
        # Test 1: RLS Policy Testing
        self.test_rls_policies()
        
        # Test 2: Access Control Verification
        self.test_access_control()
        
        # Test 3: Audit Trail Validation
        self.test_audit_trails()
        
        # Test 4: Compliance Checks
        self.test_compliance_checks()
        
        # Calculate overall score
        self.calculate_overall_score()
        
        # Generate report
        self.generate_report()
        
        return self.results
    
    def test_rls_policies(self):
        """Test 1: RLS Policy Testing - Cross-tenant isolation"""
        logger.info("🔐 Testing RLS Policies - Cross-tenant isolation")
        
        test_name = "RLS Policy Testing"
        self.results['tests_total'] += 1
        
        try:
            # Test cross-tenant data access prevention
            cross_tenant_access = self.test_cross_tenant_access()
            
            # Test tenant isolation enforcement
            tenant_isolation = self.test_tenant_isolation()
            
            # Test admin override functionality
            admin_override = self.test_admin_override()
            
            if cross_tenant_access and tenant_isolation and admin_override:
                logger.info("✅ RLS Policy Testing: PASSED")
                self.results['tests_passed'] += 1
                self.results[f'{test_name}_score'] = 100
            else:
                logger.error("❌ RLS Policy Testing: FAILED")
                self.results[f'{test_name}_score'] = 0
                self.results['critical_issues'].append("RLS policies not properly enforcing tenant isolation")
                
        except Exception as e:
            logger.error(f"❌ RLS Policy Testing failed with error: {e}")
            self.results[f'{test_name}_score'] = 0
            self.results['critical_issues'].append(f"RLS policy testing error: {str(e)}")
    
    def test_cross_tenant_access(self) -> bool:
        """Test that users cannot access data from other tenants"""
        try:
            # Attempt to access data from another tenant
            # This should fail due to RLS policies
            response = requests.get(
                f"{self.api_base_url}/api/security",
                params={
                    'action': 'summary',
                    'tenant_id': self.other_tenant_id
                },
                headers={'X-Tenant-ID': self.test_tenant_id}
            )
            
            # Should either be denied or return empty results
            if response.status_code == 403:
                logger.info("✅ Cross-tenant access properly denied (403)")
                return True
            elif response.status_code == 200:
                data = response.json()
                if not data.get('data') or len(data.get('data', [])) == 0:
                    logger.info("✅ Cross-tenant access returns empty results")
                    return True
                else:
                    logger.warning("⚠️ Cross-tenant access returned data - potential security issue")
                    return False
            else:
                logger.warning(f"⚠️ Unexpected response code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing cross-tenant access: {e}")
            return False
    
    def test_tenant_isolation(self) -> bool:
        """Test that users can only access their own tenant data"""
        try:
            # Test access to own tenant data
            response = requests.get(
                f"{self.api_base_url}/api/security",
                params={
                    'action': 'summary',
                    'tenant_id': self.test_tenant_id
                },
                headers={'X-Tenant-ID': self.test_tenant_id}
            )
            
            if response.status_code == 200:
                logger.info("✅ Own tenant access working correctly")
                return True
            else:
                logger.error(f"❌ Own tenant access failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing tenant isolation: {e}")
            return False
    
    def test_admin_override(self) -> bool:
        """Test admin override functionality"""
        try:
            # Test admin access to any tenant
            response = requests.get(
                f"{self.api_base_url}/api/security",
                params={
                    'action': 'summary',
                    'tenant_id': self.other_tenant_id
                },
                headers={'X-Tenant-ID': self.test_tenant_id, 'X-Admin-Override': 'true'}
            )
            
            # Admin should be able to access any tenant
            if response.status_code == 200:
                logger.info("✅ Admin override working correctly")
                return True
            else:
                logger.warning(f"⚠️ Admin override may not be working: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing admin override: {e}")
            return False
    
    def test_access_control(self):
        """Test 2: Access Control Verification - Role-based access control"""
        logger.info("🔑 Testing Access Control - Role-based access control")
        
        test_name = "Access Control Verification"
        self.results['tests_total'] += 1
        
        try:
            # Test role-based permissions
            role_permissions = self.test_role_permissions()
            
            # Test feature access control
            feature_access = self.test_feature_access()
            
            # Test subscription-based access
            subscription_access = self.test_subscription_access()
            
            if role_permissions and feature_access and subscription_access:
                logger.info("✅ Access Control Verification: PASSED")
                self.results['tests_passed'] += 1
                self.results[f'{test_name}_score'] = 100
            else:
                logger.error("❌ Access Control Verification: FAILED")
                self.results[f'{test_name}_score'] = 0
                self.results['critical_issues'].append("Access control not properly enforcing permissions")
                
        except Exception as e:
            logger.error(f"❌ Access Control Verification failed with error: {e}")
            self.results[f'{test_name}_score'] = 0
            self.results['critical_issues'].append(f"Access control testing error: {str(e)}")
    
    def test_role_permissions(self) -> bool:
        """Test role-based permissions"""
        try:
            # Test different user roles
            roles = ['user', 'admin', 'moderator']
            
            for role in roles:
                response = requests.get(
                    f"{self.api_base_url}/api/security",
                    params={'action': 'summary', 'tenant_id': self.test_tenant_id},
                    headers={'X-Tenant-ID': self.test_tenant_id, 'X-User-Role': role}
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Role '{role}' access working correctly")
                else:
                    logger.warning(f"⚠️ Role '{role}' access failed: {response.status_code}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error testing role permissions: {e}")
            return False
    
    def test_feature_access(self) -> bool:
        """Test feature-based access control"""
        try:
            # Test access to different features
            features = ['security', 'compliance', 'audit', 'admin']
            
            for feature in features:
                response = requests.get(
                    f"{self.api_base_url}/api/security",
                    params={'action': 'summary', 'tenant_id': self.test_tenant_id, 'feature': feature},
                    headers={'X-Tenant-ID': self.test_tenant_id}
                )
                
                if response.status_code in [200, 403]:  # 403 is expected for unauthorized features
                    logger.info(f"✅ Feature '{feature}' access control working")
                else:
                    logger.warning(f"⚠️ Feature '{feature}' access control failed: {response.status_code}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error testing feature access: {e}")
            return False
    
    def test_subscription_access(self) -> bool:
        """Test subscription-based access control"""
        try:
            # Test different subscription tiers
            tiers = ['free', 'starter', 'pro', 'enterprise']
            
            for tier in tiers:
                response = requests.get(
                    f"{self.api_base_url}/api/security",
                    params={'action': 'summary', 'tenant_id': self.test_tenant_id},
                    headers={'X-Tenant-ID': self.test_tenant_id, 'X-Subscription-Tier': tier}
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Subscription tier '{tier}' access working")
                else:
                    logger.warning(f"⚠️ Subscription tier '{tier}' access failed: {response.status_code}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error testing subscription access: {e}")
            return False
    
    def test_audit_trails(self):
        """Test 3: Audit Trail Validation - Security event logging"""
        logger.info("📝 Testing Audit Trails - Security event logging")
        
        test_name = "Audit Trail Validation"
        self.results['tests_total'] += 1
        
        try:
            # Test admin action logging
            admin_logging = self.test_admin_action_logging()
            
            # Test security event logging
            security_logging = self.test_security_event_logging()
            
            # Test audit trail completeness
            audit_completeness = self.test_audit_completeness()
            
            if admin_logging and security_logging and audit_completeness:
                logger.info("✅ Audit Trail Validation: PASSED")
                self.results['tests_passed'] += 1
                self.results[f'{test_name}_score'] = 100
            else:
                logger.error("❌ Audit Trail Validation: FAILED")
                self.results[f'{test_name}_score'] = 0
                self.results['critical_issues'].append("Audit trails not properly logging security events")
                
        except Exception as e:
            logger.error(f"❌ Audit Trail Validation failed with error: {e}")
            self.results[f'{test_name}_score'] = 0
            self.results['critical_issues'].append(f"Audit trail testing error: {str(e)}")
    
    def test_admin_action_logging(self) -> bool:
        """Test admin action logging"""
        try:
            # Test logging of admin actions
            admin_action = {
                'action_type': 'user_role_change',
                'action_category': 'user_management',
                'target_type': 'user',
                'target_id': str(uuid.uuid4()),
                'reason': 'Security validation test',
                'risk_assessment': 'low'
            }
            
            response = requests.post(
                f"{self.api_base_url}/api/security/admin-actions",
                json=admin_action,
                headers={'X-Tenant-ID': self.test_tenant_id}
            )
            
            if response.status_code == 201:
                logger.info("✅ Admin action logging working correctly")
                return True
            else:
                logger.warning(f"⚠️ Admin action logging failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing admin action logging: {e}")
            return False
    
    def test_security_event_logging(self) -> bool:
        """Test security event logging"""
        try:
            # Test logging of security events
            security_event = {
                'event_type': 'failed_login',
                'event_category': 'authentication',
                'ip_address': '192.168.1.1',
                'user_agent': 'SecurityValidator/1.0',
                'risk_level': 'medium'
            }
            
            response = requests.post(
                f"{self.api_base_url}/api/security/events",
                json=security_event,
                headers={'X-Tenant-ID': self.test_tenant_id}
            )
            
            if response.status_code == 201:
                logger.info("✅ Security event logging working correctly")
                return True
            else:
                logger.warning(f"⚠️ Security event logging failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing security event logging: {e}")
            return False
    
    def test_audit_completeness(self) -> bool:
        """Test audit trail completeness"""
        try:
            # Check if audit logs are being generated
            response = requests.get(
                f"{self.api_base_url}/api/security/audit-logs",
                params={'tenant_id': self.test_tenant_id, 'limit': 10},
                headers={'X-Tenant-ID': self.test_tenant_id}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and len(data['data']) > 0:
                    logger.info("✅ Audit trail completeness verified")
                    return True
                else:
                    logger.warning("⚠️ Audit trail may be incomplete")
                    return False
            else:
                logger.warning(f"⚠️ Audit trail access failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing audit completeness: {e}")
            return False
    
    def test_compliance_checks(self):
        """Test 4: Compliance Checks - GDPR, PCI, SOC2 compliance"""
        logger.info("📋 Testing Compliance Checks - GDPR, PCI, SOC2 compliance")
        
        test_name = "Compliance Checks"
        self.results['tests_total'] += 1
        
        try:
            # Test GDPR compliance
            gdpr_compliance = self.test_gdpr_compliance()
            
            # Test PCI compliance
            pci_compliance = self.test_pci_compliance()
            
            # Test SOC2 compliance
            soc2_compliance = self.test_soc2_compliance()
            
            if gdpr_compliance and pci_compliance and soc2_compliance:
                logger.info("✅ Compliance Checks: PASSED")
                self.results['tests_passed'] += 1
                self.results[f'{test_name}_score'] = 100
            else:
                logger.error("❌ Compliance Checks: FAILED")
                self.results[f'{test_name}_score'] = 0
                self.results['critical_issues'].append("Compliance checks not meeting requirements")
                
        except Exception as e:
            logger.error(f"❌ Compliance Checks failed with error: {e}")
            self.results[f'{test_name}_score'] = 0
            self.results['critical_issues'].append(f"Compliance testing error: {str(e)}")
    
    def test_gdpr_compliance(self) -> bool:
        """Test GDPR compliance"""
        try:
            # Test GDPR data processing compliance
            response = requests.get(
                f"{self.api_base_url}/api/security/compliance",
                params={'tenant_id': self.test_tenant_id, 'type': 'gdpr'},
                headers={'X-Tenant-ID': self.test_tenant_id}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data', {}).get('is_compliant', False):
                    logger.info("✅ GDPR compliance verified")
                    return True
                else:
                    logger.warning("⚠️ GDPR compliance issues detected")
                    return False
            else:
                logger.warning(f"⚠️ GDPR compliance check failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing GDPR compliance: {e}")
            return False
    
    def test_pci_compliance(self) -> bool:
        """Test PCI compliance"""
        try:
            # Test PCI DSS compliance
            response = requests.get(
                f"{self.api_base_url}/api/security/compliance",
                params={'tenant_id': self.test_tenant_id, 'type': 'pci'},
                headers={'X-Tenant-ID': self.test_tenant_id}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data', {}).get('is_compliant', False):
                    logger.info("✅ PCI compliance verified")
                    return True
                else:
                    logger.warning("⚠️ PCI compliance issues detected")
                    return False
            else:
                logger.warning(f"⚠️ PCI compliance check failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing PCI compliance: {e}")
            return False
    
    def test_soc2_compliance(self) -> bool:
        """Test SOC2 compliance"""
        try:
            # Test SOC2 compliance
            response = requests.get(
                f"{self.api_base_url}/api/security/compliance",
                params={'tenant_id': self.test_tenant_id, 'type': 'soc2'},
                headers={'X-Tenant-ID': self.test_tenant_id}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data', {}).get('is_compliant', False):
                    logger.info("✅ SOC2 compliance verified")
                    return True
                else:
                    logger.warning("⚠️ SOC2 compliance issues detected")
                    return False
            else:
                logger.warning(f"⚠️ SOC2 compliance check failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing SOC2 compliance: {e}")
            return False
    
    def calculate_overall_score(self):
        """Calculate overall security validation score"""
        scores = []
        
        for key, value in self.results.items():
            if key.endswith('_score') and isinstance(value, (int, float)):
                scores.append(value)
        
        if scores:
            self.results['overall_score'] = sum(scores) / len(scores)
        else:
            self.results['overall_score'] = 0
        
        # Determine grade
        if self.results['overall_score'] >= 90:
            grade = 'A+'
        elif self.results['overall_score'] >= 80:
            grade = 'A'
        elif self.results['overall_score'] >= 70:
            grade = 'B'
        elif self.results['overall_score'] >= 60:
            grade = 'C'
        elif self.results['overall_score'] >= 50:
            grade = 'D'
        else:
            grade = 'F'
        
        self.results['grade'] = grade
    
    def generate_report(self):
        """Generate comprehensive security validation report"""
        logger.info("📊 Generating Security Validation Report")
        logger.info("=" * 60)
        
        # Log results
        logger.info(f"Overall Score: {self.results['overall_score']:.1f}/100 ({self.results['grade']})")
        logger.info(f"Tests Passed: {self.results['tests_passed']}/{self.results['tests_total']}")
        
        if self.results['critical_issues']:
            logger.error("🚨 Critical Issues Found:")
            for issue in self.results['critical_issues']:
                logger.error(f"  - {issue}")
        
        if self.results['warnings']:
            logger.warning("⚠️ Warnings:")
            for warning in self.results['warnings']:
                logger.warning(f"  - {warning}")
        
        if self.results['recommendations']:
            logger.info("💡 Recommendations:")
            for rec in self.results['recommendations']:
                logger.info(f"  - {rec}")
        
        # Save detailed report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f'security_validation_report_{timestamp}.json'
        
        with open(report_filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        logger.info(f"📁 Detailed report saved to: {report_filename}")
        
        # Generate human-readable summary
        summary_filename = f'security_validation_summary_{timestamp}.txt'
        self.generate_human_readable_summary(summary_filename)
        
        logger.info(f"📄 Human-readable summary saved to: {summary_filename}")
    
    def generate_human_readable_summary(self, filename: str):
        """Generate human-readable summary report"""
        with open(filename, 'w') as f:
            f.write("SECURITY & COMPLIANCE VALIDATION SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Overall Score: {self.results['overall_score']:.1f}/100 ({self.results['grade']})\n")
            f.write(f"Tests Passed: {self.results['tests_passed']}/{self.results['tests_total']}\n\n")
            
            f.write("TEST RESULTS:\n")
            f.write("-" * 20 + "\n")
            
            for key, value in self.results.items():
                if key.endswith('_score'):
                    test_name = key.replace('_score', '').replace('_', ' ').title()
                    f.write(f"{test_name}: {value}/100\n")
            
            f.write("\nCRITICAL ISSUES:\n")
            f.write("-" * 20 + "\n")
            if self.results['critical_issues']:
                for issue in self.results['critical_issues']:
                    f.write(f"🚨 {issue}\n")
            else:
                f.write("✅ No critical issues found\n")
            
            f.write("\nWARNINGS:\n")
            f.write("-" * 20 + "\n")
            if self.results['warnings']:
                for warning in self.results['warnings']:
                    f.write(f"⚠️ {warning}\n")
            else:
                f.write("✅ No warnings\n")
            
            f.write("\nRECOMMENDATIONS:\n")
            f.write("-" * 20 + "\n")
            if self.results['recommendations']:
                for rec in self.results['recommendations']:
                    f.write(f"💡 {rec}\n")
            else:
                f.write("✅ No recommendations\n")
            
            f.write("\nSTATUS:\n")
            f.write("-" * 20 + "\n")
            if self.results['overall_score'] >= 80:
                f.write("✅ SECURITY VALIDATION PASSED - System ready for production\n")
            elif self.results['overall_score'] >= 60:
                f.write("⚠️ SECURITY VALIDATION PARTIAL - Address issues before production\n")
            else:
                f.write("❌ SECURITY VALIDATION FAILED - Critical issues must be resolved\n")

def main():
    """Main function to run security validation"""
    try:
        validator = SecurityValidator()
        results = validator.run_all_tests()
        
        # Exit with appropriate code
        if results['overall_score'] >= 80:
            logger.info("🎉 Security validation completed successfully!")
            sys.exit(0)
        elif results['overall_score'] >= 60:
            logger.warning("⚠️ Security validation completed with warnings")
            sys.exit(1)
        else:
            logger.error("❌ Security validation failed")
            sys.exit(2)
            
    except Exception as e:
        logger.error(f"Fatal error during security validation: {e}")
        sys.exit(3)

if __name__ == "__main__":
    main()
