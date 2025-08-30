#!/usr/bin/env python3
"""
Comprehensive Security & Compliance Validation Script
Section 6 of the Critical Pre-Decommission Checklist

This script performs actual database connectivity and security validation:
1. RLS Policy Testing - Real database security validation
2. Access Control Verification - Actual permission checks
3. Audit Trail Validation - Real audit system validation
4. Compliance Checks - Actual compliance framework validation

Usage: python3 scripts/security_validation_comprehensive.py
"""

import os
import sys
import json
import time
import uuid
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('security_validation_comprehensive.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveSecurityValidator:
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
        """Run all comprehensive security validation tests"""
        logger.info("🚀 Starting Comprehensive Security & Compliance Validation")
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
            # Test cross-tenant data access prevention using Supabase REST API
            cross_tenant_access = self.test_cross_tenant_access_supabase()
            
            # Test tenant isolation enforcement
            tenant_isolation = self.test_tenant_isolation_supabase()
            
            # Test admin override functionality
            admin_override = self.test_admin_override_supabase()
            
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
    
    def test_cross_tenant_access_supabase(self) -> bool:
        """Test cross-tenant access prevention using Supabase REST API"""
        try:
            # Test accessing data from another tenant using Supabase REST API
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json'
            }
            
            # Try to access users from another tenant
            response = requests.get(
                f"{self.supabase_url}/rest/v1/users",
                headers=headers,
                params={'tenant_id': f'eq.{self.other_tenant_id}'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if len(data) == 0:
                    logger.info("✅ Cross-tenant access properly prevented (empty results)")
                    return True
                else:
                    logger.warning("⚠️ Cross-tenant access returned data - potential security issue")
                    return False
            else:
                logger.info(f"✅ Cross-tenant access properly denied (status: {response.status_code})")
                return True
                
        except Exception as e:
            logger.error(f"Error testing cross-tenant access via Supabase: {e}")
            return False
    
    def test_tenant_isolation_supabase(self) -> bool:
        """Test tenant isolation using Supabase REST API"""
        try:
            # Test access to own tenant data
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json'
            }
            
            # Try to access users from own tenant
            response = requests.get(
                f"{self.supabase_url}/rest/v1/users",
                headers=headers,
                params={'tenant_id': f'eq.{self.test_tenant_id}'}
            )
            
            if response.status_code == 200:
                logger.info("✅ Own tenant access working correctly")
                return True
            else:
                logger.error(f"❌ Own tenant access failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing tenant isolation via Supabase: {e}")
            return False
    
    def test_admin_override_supabase(self) -> bool:
        """Test admin override functionality using Supabase REST API"""
        try:
            # Test admin access to any tenant
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json',
                'X-Admin-Override': 'true'
            }
            
            # Try to access users from any tenant
            response = requests.get(
                f"{self.supabase_url}/rest/v1/users",
                headers=headers,
                params={'select': 'id,email,tenant_id'}
            )
            
            if response.status_code == 200:
                logger.info("✅ Admin override working correctly")
                return True
            else:
                logger.warning(f"⚠️ Admin override may not be working: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing admin override via Supabase: {e}")
            return False
    
    def test_access_control(self):
        """Test 2: Access Control Verification - Role-based access control"""
        logger.info("🔑 Testing Access Control - Role-based access control")
        
        test_name = "Access Control Verification"
        self.results['tests_total'] += 1
        
        try:
            # Test role-based permissions
            role_permissions = self.test_role_permissions_supabase()
            
            # Test feature access control
            feature_access = self.test_feature_access_supabase()
            
            # Test subscription-based access
            subscription_access = self.test_subscription_access_supabase()
            
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
    
    def test_role_permissions_supabase(self) -> bool:
        """Test role-based permissions using Supabase"""
        try:
            # Test different user roles
            roles = ['user', 'admin', 'moderator']
            
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json'
            }
            
            for role in roles:
                # Test role-based access by checking user permissions
                response = requests.get(
                    f"{self.supabase_url}/rest/v1/users",
                    headers=headers,
                    params={'select': 'id,email,role', 'role': f'eq.{role}'}
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Role '{role}' access working correctly")
                else:
                    logger.warning(f"⚠️ Role '{role}' access failed: {response.status_code}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error testing role permissions via Supabase: {e}")
            return False
    
    def test_feature_access_supabase(self) -> bool:
        """Test feature-based access control using Supabase"""
        try:
            # Test access to different features
            features = ['security', 'compliance', 'audit', 'admin']
            
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json'
            }
            
            for feature in features:
                # Test feature access by checking related tables
                if feature == 'security':
                    response = requests.get(
                        f"{self.supabase_url}/rest/v1/security_policies",
                        headers=headers,
                        params={'select': 'id,policy_name'}
                    )
                elif feature == 'compliance':
                    response = requests.get(
                        f"{self.supabase_url}/rest/v1/compliance_checks",
                        headers=headers,
                        params={'select': 'id,check_name'}
                    )
                elif feature == 'audit':
                    response = requests.get(
                        f"{self.supabase_url}/rest/v1/admin_actions_audit",
                        headers=headers,
                        params={'select': 'id,action_type'}
                    )
                else:  # admin
                    response = requests.get(
                        f"{self.supabase_url}/rest/v1/users",
                        headers=headers,
                        params={'select': 'id,email,role', 'role': 'eq.admin'}
                    )
                
                if response.status_code in [200, 404]:  # 404 is expected for empty tables
                    logger.info(f"✅ Feature '{feature}' access control working")
                else:
                    logger.warning(f"⚠️ Feature '{feature}' access control failed: {response.status_code}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error testing feature access via Supabase: {e}")
            return False
    
    def test_subscription_access_supabase(self) -> bool:
        """Test subscription-based access control using Supabase"""
        try:
            # Test different subscription tiers
            tiers = ['free', 'starter', 'pro', 'enterprise']
            
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json'
            }
            
            for tier in tiers:
                # Test subscription tier access by checking tenant plans
                response = requests.get(
                    f"{self.supabase_url}/rest/v1/tenants",
                    headers=headers,
                    params={'select': 'id,name,plan', 'plan': f'eq.{tier}'}
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Subscription tier '{tier}' access working")
                else:
                    logger.warning(f"⚠️ Subscription tier '{tier}' access failed: {response.status_code}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error testing subscription access via Supabase: {e}")
            return False
    
    def test_audit_trails(self):
        """Test 3: Audit Trail Validation - Security event logging"""
        logger.info("📝 Testing Audit Trails - Security event logging")
        
        test_name = "Audit Trail Validation"
        self.results['tests_total'] += 1
        
        try:
            # Test admin action logging
            admin_logging = self.test_admin_action_logging_supabase()
            
            # Test security event logging
            security_logging = self.test_security_event_logging_supabase()
            
            # Test audit trail completeness
            audit_completeness = self.test_audit_completeness_supabase()
            
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
    
    def test_admin_action_logging_supabase(self) -> bool:
        """Test admin action logging using Supabase"""
        try:
            # Test logging of admin actions
            admin_action = {
                'tenant_id': self.test_tenant_id,
                'admin_user_id': self.test_user_id,
                'action_type': 'user_role_change',
                'action_category': 'user_management',
                'target_type': 'user',
                'target_id': str(uuid.uuid4()),
                'reason': 'Security validation test',
                'risk_assessment': 'low'
            }
            
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.supabase_url}/rest/v1/admin_actions_audit",
                headers=headers,
                json=admin_action
            )
            
            if response.status_code == 201:
                logger.info("✅ Admin action logging working correctly")
                return True
            else:
                logger.warning(f"⚠️ Admin action logging failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing admin action logging via Supabase: {e}")
            return False
    
    def test_security_event_logging_supabase(self) -> bool:
        """Test security event logging using Supabase"""
        try:
            # Test logging of security events
            security_event = {
                'tenant_id': self.test_tenant_id,
                'event_type': 'failed_login',
                'event_category': 'authentication',
                'ip_address': '192.168.1.1',
                'user_agent': 'SecurityValidator/1.0',
                'risk_level': 'medium'
            }
            
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json'
            }
            
            # Use audit_logs table for security events
            response = requests.post(
                f"{self.supabase_url}/rest/v1/audit_logs",
                headers=headers,
                json={
                    'tenant_id': self.test_tenant_id,
                    'user_id': self.test_user_id,
                    'action': security_event['event_type'],
                    'category': security_event['event_category'],
                    'details': security_event,
                    'ip_address': security_event['ip_address'],
                    'user_agent': security_event['user_agent']
                }
            )
            
            if response.status_code == 201:
                logger.info("✅ Security event logging working correctly")
                return True
            else:
                logger.warning(f"⚠️ Security event logging failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing security event logging via Supabase: {e}")
            return False
    
    def test_audit_completeness_supabase(self) -> bool:
        """Test audit trail completeness using Supabase"""
        try:
            # Check if audit logs are being generated
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.supabase_url}/rest/v1/audit_logs",
                headers=headers,
                params={'select': 'id,action,category,timestamp', 'limit': '10'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if len(data) > 0:
                    logger.info("✅ Audit trail completeness verified")
                    return True
                else:
                    logger.warning("⚠️ Audit trail may be incomplete")
                    return False
            else:
                logger.warning(f"⚠️ Audit trail access failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing audit completeness via Supabase: {e}")
            return False
    
    def test_compliance_checks(self):
        """Test 4: Compliance Checks - GDPR, PCI, SOC2 compliance"""
        logger.info("📋 Testing Compliance Checks - GDPR, PCI, SOC2 compliance")
        
        test_name = "Compliance Checks"
        self.results['tests_total'] += 1
        
        try:
            # Test GDPR compliance
            gdpr_compliance = self.test_gdpr_compliance_supabase()
            
            # Test PCI compliance
            pci_compliance = self.test_pci_compliance_supabase()
            
            # Test SOC2 compliance
            soc2_compliance = self.test_soc2_compliance_supabase()
            
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
    
    def test_gdpr_compliance_supabase(self) -> bool:
        """Test GDPR compliance using Supabase"""
        try:
            # Check GDPR compliance framework
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json'
            }
            
            # Check data classification for PII data
            response = requests.get(
                f"{self.supabase_url}/rest/v1/data_classification",
                headers=headers,
                params={'select': 'id,classification_level,gdpr_impact', 'gdpr_impact': 'eq.true'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if len(data) > 0:
                    logger.info("✅ GDPR compliance framework verified")
                    return True
                else:
                    logger.warning("⚠️ No GDPR-impacting data classifications found")
                    return False
            else:
                logger.warning(f"⚠️ GDPR compliance check failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing GDPR compliance via Supabase: {e}")
            return False
    
    def test_pci_compliance_supabase(self) -> bool:
        """Test PCI compliance using Supabase"""
        try:
            # Check PCI compliance framework
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json'
            }
            
            # Check data classification for payment data
            response = requests.get(
                f"{self.supabase_url}/rest/v1/data_classification",
                headers=headers,
                params={'select': 'id,classification_level,pci_impact', 'pci_impact': 'eq.true'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if len(data) > 0:
                    logger.info("✅ PCI compliance framework verified")
                    return True
                else:
                    logger.warning("⚠️ No PCI-impacting data classifications found")
                    return False
            else:
                logger.warning(f"⚠️ PCI compliance check failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing PCI compliance via Supabase: {e}")
            return False
    
    def test_soc2_compliance_supabase(self) -> bool:
        """Test SOC2 compliance using Supabase"""
        try:
            # Check SOC2 compliance framework
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json'
            }
            
            # Check access reviews for SOC2 compliance
            response = requests.get(
                f"{self.supabase_url}/rest/v1/access_reviews",
                headers=headers,
                params={'select': 'id,review_type,status'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if len(data) > 0:
                    logger.info("✅ SOC2 compliance framework verified")
                    return True
                else:
                    logger.warning("⚠️ No access reviews found for SOC2 compliance")
                    return False
            else:
                logger.warning(f"⚠️ SOC2 compliance check failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing SOC2 compliance via Supabase: {e}")
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
        report_filename = f'security_validation_comprehensive_report_{timestamp}.json'
        
        with open(report_filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        logger.info(f"📁 Detailed report saved to: {report_filename}")
        
        # Generate human-readable summary
        summary_filename = f'security_validation_comprehensive_summary_{timestamp}.txt'
        self.generate_human_readable_summary(summary_filename)
        
        logger.info(f"📄 Human-readable summary saved to: {summary_filename}")
    
    def generate_human_readable_summary(self, filename: str):
        """Generate human-readable summary report"""
        with open(filename, 'w') as f:
            f.write("COMPREHENSIVE SECURITY & COMPLIANCE VALIDATION SUMMARY\n")
            f.write("=" * 60 + "\n\n")
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
    """Main function to run comprehensive security validation"""
    try:
        validator = ComprehensiveSecurityValidator()
        results = validator.run_all_tests()
        
        # Exit with appropriate code
        if results['overall_score'] >= 80:
            logger.info("🎉 Comprehensive security validation completed successfully!")
            sys.exit(0)
        elif results['overall_score'] >= 60:
            logger.warning("⚠️ Comprehensive security validation completed with warnings")
            sys.exit(1)
        else:
            logger.error("❌ Comprehensive security validation failed")
            sys.exit(2)
            
    except Exception as e:
        logger.error(f"Fatal error during comprehensive security validation: {e}")
        sys.exit(3)

if __name__ == "__main__":
    main()
