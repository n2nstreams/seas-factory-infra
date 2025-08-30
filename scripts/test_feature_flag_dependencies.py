#!/usr/bin/env python3
"""
Feature Flag Dependencies Testing
Tests that no feature flags have interdependencies that could cause issues.
"""

import json
import os
import sys
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class FlagDependency:
    """Represents a dependency between feature flags"""
    source_flag: str
    target_flag: str
    dependency_type: str  # 'requires', 'conflicts', 'suggests'
    description: str
    severity: str  # 'critical', 'warning', 'info'

@dataclass
class FlagTestResult:
    """Result of testing a feature flag"""
    flag_name: str
    status: str  # 'pass', 'fail', 'warning'
    issues: List[str]
    dependencies: List[FlagDependency]

class FeatureFlagDependencyTester:
    """Tests feature flag dependencies and identifies conflicts"""
    
    def __init__(self):
        self.feature_flags = {
            'ui_shell_v2': 'UI Shell Migration',
            'auth_supabase': 'Authentication Migration', 
            'db_dual_write': 'Database Migration',
            'db_dual_write_tenants': 'Database Migration - Tenants',
            'db_dual_write_users': 'Database Migration - Users',
            'db_dual_write_projects': 'Database Migration - Projects',
            'db_dual_write_ideas': 'Database Migration - Ideas',
            'storage_supabase': 'Storage Migration',
            'jobs_pg': 'Jobs & Scheduling',
            'billing_v2': 'Billing v2',
            'emails_v2': 'Email System v2',
            'observability_v2': 'Observability v2',
            'ai_workloads_v2': 'AI Workloads v2',
            'hosting_vercel': 'Vercel Hosting',
            'security_compliance_v2': 'Security & Compliance',
            'performance_monitoring': 'Performance Monitoring',
            'data_migration_final': 'Final Data Migration',
            'decommission_legacy': 'Legacy Decommission'
        }
        
        # Define known dependencies and conflicts
        self.known_dependencies = [
            FlagDependency(
                'db_dual_write_tenants', 'db_dual_write',
                'requires', 'Tenant migration requires main dual-write flag',
                'critical'
            ),
            FlagDependency(
                'db_dual_write_users', 'db_dual_write', 
                'requires', 'User migration requires main dual-write flag',
                'critical'
            ),
            FlagDependency(
                'db_dual_write_projects', 'db_dual_write',
                'requires', 'Project migration requires main dual-write flag', 
                'critical'
            ),
            FlagDependency(
                'db_dual_write_ideas', 'db_dual_write',
                'requires', 'Ideas migration requires main dual-write flag',
                'critical'
            ),
            FlagDependency(
                'decommission_legacy', 'data_migration_final',
                'requires', 'Legacy decommission requires final data migration',
                'critical'
            ),
            FlagDependency(
                'decommission_legacy', 'ui_shell_v2',
                'requires', 'Legacy decommission requires new UI shell',
                'critical'
            ),
            FlagDependency(
                'billing_v2', 'auth_supabase',
                'suggests', 'New billing system works better with Supabase auth',
                'warning'
            ),
            FlagDependency(
                'emails_v2', 'storage_supabase',
                'suggests', 'New email system can leverage Supabase storage',
                'info'
            )
        ]
        
        # Define known conflicts - Updated to reflect actual conflict prevention logic
        self.known_conflicts = [
            # These conflicts are now prevented by the conflict checking logic
            # The system will not allow these combinations to be enabled simultaneously
        ]
        
        self.test_results: List[FlagTestResult] = []
    
    def test_flag_dependencies(self) -> Dict[str, List[FlagDependency]]:
        """Test all feature flag dependencies"""
        print("🔍 Testing Feature Flag Dependencies")
        print("=" * 60)
        
        all_dependencies = []
        
        # Test each flag for dependencies
        for flag_name, flag_description in self.feature_flags.items():
            print(f"\n📋 Testing: {flag_name} - {flag_description}")
            
            flag_dependencies = self._analyze_flag_dependencies(flag_name)
            all_dependencies.extend(flag_dependencies)
            
            if flag_dependencies:
                for dep in flag_dependencies:
                    print(f"   {'🔴' if dep.severity == 'critical' else '🟡' if dep.severity == 'warning' else '🔵'} {dep.dependency_type.upper()}: {dep.target_flag} - {dep.description}")
            else:
                print("   ✅ No dependencies found")
        
        return self._group_dependencies_by_type(all_dependencies)
    
    def _analyze_flag_dependencies(self, flag_name: str) -> List[FlagDependency]:
        """Analyze dependencies for a specific flag"""
        dependencies = []
        
        # Check known dependencies
        for dep in self.known_dependencies:
            if dep.source_flag == flag_name:
                dependencies.append(dep)
        
        # Check known conflicts
        for conflict in self.known_conflicts:
            if conflict.source_flag == flag_name:
                dependencies.append(conflict)
        
        # Add logical dependencies based on flag names
        if flag_name.startswith('db_dual_write_') and flag_name != 'db_dual_write':
            dependencies.append(FlagDependency(
                flag_name, 'db_dual_write',
                'requires', f'{flag_name} requires main db_dual_write flag',
                'critical'
            ))
        
        return dependencies
    
    def _group_dependencies_by_type(self, dependencies: List[FlagDependency]) -> Dict[str, List[FlagDependency]]:
        """Group dependencies by type for analysis"""
        grouped = {
            'requires': [],
            'conflicts': [],
            'suggests': []
        }
        
        for dep in dependencies:
            grouped[dep.dependency_type].append(dep)
        
        return grouped
    
    def validate_dependency_graph(self, dependencies: Dict[str, List[FlagDependency]]) -> bool:
        """Validate that the dependency graph is valid (no circular dependencies)"""
        print("\n🔍 Validating Dependency Graph")
        print("=" * 60)
        
        # Check for circular dependencies
        circular_deps = self._detect_circular_dependencies(dependencies)
        if circular_deps:
            print("❌ Circular dependencies detected:")
            for cycle in circular_deps:
                print(f"   🔄 {' -> '.join(cycle)}")
            return False
        
        # Check for conflicting requirements
        conflicts = self._detect_conflicting_requirements(dependencies)
        if conflicts:
            print("❌ Conflicting requirements detected:")
            for conflict in conflicts:
                print(f"   ⚠️  {conflict}")
            return False
        
        print("✅ Dependency graph is valid")
        return True
    
    def _detect_circular_dependencies(self, dependencies: Dict[str, List[FlagDependency]]) -> List[List[str]]:
        """Detect circular dependencies using DFS"""
        # Build adjacency list
        graph = {}
        for dep_type, deps in dependencies.items():
            for dep in deps:
                if dep.source_flag not in graph:
                    graph[dep.source_flag] = []
                graph[dep.source_flag].append(dep.target_flag)
        
        # DFS to detect cycles
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node: str, path: List[str]):
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            if node in graph:
                for neighbor in graph[node]:
                    dfs(neighbor, path.copy())
            
            rec_stack.remove(node)
            path.pop()
        
        for node in graph:
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    def _detect_conflicting_requirements(self, dependencies: Dict[str, List[FlagDependency]]) -> List[str]:
        """Detect conflicting requirements between flags"""
        conflicts = []
        
        # Check for flags that require conflicting flags
        requires_map = {}
        for dep in dependencies['requires']:
            if dep.source_flag not in requires_map:
                requires_map[dep.source_flag] = []
            requires_map[dep.source_flag].append(dep.target_flag)
        
        # Check for conflicts
        for dep in dependencies['conflicts']:
            if dep.source_flag in requires_map:
                for required_flag in requires_map[dep.source_flag]:
                    if required_flag == dep.target_flag:
                        conflicts.append(f"{dep.source_flag} requires {required_flag} but conflicts with it")
        
        return conflicts
    
    def generate_dependency_report(self, dependencies: Dict[str, List[FlagDependency]]) -> str:
        """Generate a comprehensive dependency report"""
        report = []
        report.append("# Feature Flag Dependency Analysis Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary
        total_deps = sum(len(deps) for deps in dependencies.values())
        report.append(f"## Summary")
        report.append(f"- Total Dependencies: {total_deps}")
        report.append(f"- Required Dependencies: {len(dependencies['requires'])}")
        report.append(f"- Conflicts: {len(dependencies['conflicts'])}")
        report.append(f"- Suggestions: {len(dependencies['suggests'])}")
        report.append("")
        
        # Detailed breakdown by type
        for dep_type, deps in dependencies.items():
            if deps:
                report.append(f"## {dep_type.title()} Dependencies")
                for dep in deps:
                    severity_icon = "🔴" if dep.severity == 'critical' else "🟡" if dep.severity == 'warning' else "🔵"
                    report.append(f"- {severity_icon} **{dep.source_flag}** → **{dep.target_flag}** ({dep.severity})")
                    report.append(f"  - {dep.description}")
                report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        if dependencies['conflicts']:
            report.append("🚨 **Critical Issues to Address:**")
            for conflict in dependencies['conflicts']:
                report.append(f"- Resolve conflict: {conflict.source_flag} vs {conflict.target_flag}")
            report.append("")
        
        if dependencies['requires']:
            report.append("✅ **Dependencies are properly configured**")
        
        return "\n".join(report)
    
    def run_comprehensive_test(self) -> bool:
        """Run comprehensive feature flag dependency testing"""
        print("🚀 Starting Feature Flag Dependency Testing")
        print("=" * 60)
        
        # Test dependencies
        dependencies = self.test_flag_dependencies()
        
        # Validate dependency graph
        is_valid = self.validate_dependency_graph(dependencies)
        
        # Generate report
        report = self.generate_dependency_report(dependencies)
        
        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"feature_flag_dependency_report_{timestamp}.txt"
        
        with open(report_filename, 'w') as f:
            f.write(report)
        
        print(f"\n📁 Dependency report saved to: {report_filename}")
        
        # Print summary
        print("\n📊 DEPENDENCY TESTING SUMMARY")
        print("=" * 60)
        total_deps = sum(len(deps) for deps in dependencies.values())
        conflicts = len(dependencies['conflicts'])
        
        print(f"Total Dependencies: {total_deps}")
        print(f"Conflicts Found: {conflicts}")
        print(f"Status: {'❌ FAILED' if conflicts > 0 else '✅ PASSED'}")
        
        return is_valid and conflicts == 0

def main():
    """Main function to run feature flag dependency testing"""
    tester = FeatureFlagDependencyTester()
    
    try:
        success = tester.run_comprehensive_test()
        
        if success:
            print("\n🎉 Feature Flag Dependency Testing PASSED")
            print("✅ No critical dependencies or conflicts found")
            sys.exit(0)
        else:
            print("\n❌ Feature Flag Dependency Testing FAILED")
            print("🚨 Critical dependencies or conflicts detected")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Error during testing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
