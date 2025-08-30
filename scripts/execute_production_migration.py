#!/usr/bin/env python3
"""
Production Migration Master Script
Orchestrates the complete production migration process
"""

import os
import sys
import logging
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProductionMigrationOrchestrator:
    """Orchestrates the complete production migration process"""
    
    def __init__(self):
        self.migration_plan = {
            "phase": "preparation",
            "started_at": None,
            "current_step": None,
            "completed_steps": [],
            "failed_steps": [],
            "overall_status": "pending"
        }
        
        self.migration_steps = [
            {
                "id": "pre_migration_validation",
                "name": "Pre-Migration Validation",
                "description": "Run final validation checks before migration",
                "script": "final_migration_validation.py",
                "required": True
            },
            {
                "id": "database_preparation",
                "name": "Database Preparation",
                "description": "Prepare Supabase for migration",
                "script": "prepare_supabase_migration.py",
                "required": True
            },
            {
                "id": "data_migration",
                "name": "Data Migration Execution",
                "description": "Execute the actual data migration",
                "script": "execute_final_migration.py",
                "required": True
            },
            {
                "id": "post_migration_validation",
                "name": "Post-Migration Validation",
                "description": "Validate migration results",
                "script": "validate_migration_results.py",
                "required": True
            },
            {
                "id": "feature_flag_activation",
                "name": "Feature Flag Activation",
                "description": "Activate migration-related feature flags",
                "script": "activate_migration_flags.py",
                "required": True
            },
            {
                "id": "legacy_decommission_prep",
                "name": "Legacy Decommission Preparation",
                "description": "Prepare for legacy system decommissioning",
                "script": "prepare_legacy_decommission.py",
                "required": False
            }
        ]
    
    async def execute_migration_plan(self):
        """Execute the complete migration plan"""
        try:
            logger.info("🚀 Starting Production Migration Process")
            logger.info("=" * 60)
            
            self.migration_plan["started_at"] = datetime.now().isoformat()
            self.migration_plan["overall_status"] = "in_progress"
            
            # Phase 1: Pre-Migration
            await self._execute_phase("pre_migration", [
                "pre_migration_validation",
                "database_preparation"
            ])
            
            # Phase 2: Migration Execution
            await self._execute_phase("migration", [
                "data_migration"
            ])
            
            # Phase 3: Post-Migration
            await self._execute_phase("post_migration", [
                "post_migration_validation",
                "feature_flag_activation"
            ])
            
            # Phase 4: Legacy Preparation
            await self._execute_phase("legacy_prep", [
                "legacy_decommission_prep"
            ])
            
            # Final status update
            if not self.migration_plan["failed_steps"]:
                self.migration_plan["overall_status"] = "completed"
                logger.info("🎉 Production Migration completed successfully!")
            else:
                self.migration_plan["overall_status"] = "completed_with_errors"
                logger.warning("⚠️ Migration completed with some errors")
            
            # Generate final report
            await self._generate_final_report()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration plan execution failed: {str(e)}")
            self.migration_plan["overall_status"] = "failed"
            return False
    
    async def _execute_phase(self, phase_name: str, step_ids: List[str]):
        """Execute a migration phase"""
        logger.info(f"🔄 Executing Phase: {phase_name.upper()}")
        logger.info("-" * 40)
        
        for step_id in step_ids:
            step = next((s for s in self.migration_steps if s["id"] == step_id), None)
            if not step:
                logger.error(f"Step {step_id} not found in migration plan")
                continue
            
            await self._execute_step(step)
        
        logger.info(f"✅ Phase {phase_name.upper()} completed")
        logger.info("")
    
    async def _execute_step(self, step: Dict[str, Any]):
        """Execute a single migration step"""
        try:
            logger.info(f"📋 Executing: {step['name']}")
            logger.info(f"   Description: {step['description']}")
            
            self.migration_plan["current_step"] = step["id"]
            
            # Check if script exists
            script_path = os.path.join("scripts", step["script"])
            if not os.path.exists(script_path):
                if step["required"]:
                    raise FileNotFoundError(f"Required script {step['script']} not found")
                else:
                    logger.info(f"   ⏭️  Skipping (script not found and not required)")
                    return
            
            # Execute script
            success = await self._run_script(script_path)
            
            if success:
                self.migration_plan["completed_steps"].append(step["id"])
                logger.info(f"   ✅ {step['name']} completed successfully")
            else:
                if step["required"]:
                    raise Exception(f"Required step {step['name']} failed")
                else:
                    self.migration_plan["failed_steps"].append(step["id"])
                    logger.warning(f"   ⚠️  {step['name']} failed (not required)")
            
        except Exception as e:
            logger.error(f"   ❌ {step['name']} failed: {str(e)}")
            self.migration_plan["failed_steps"].append(step["id"])
            
            if step["required"]:
                raise
    
    async def _run_script(self, script_path: str) -> bool:
        """Run a Python script and return success status"""
        try:
            # Import and run the script
            script_dir = os.path.dirname(script_path)
            script_name = os.path.basename(script_path)
            
            # Change to script directory
            original_dir = os.getcwd()
            os.chdir(script_dir)
            
            try:
                # Import the script module
                spec = __import__(script_name.replace('.py', ''))
                
                # Check if it has a main function
                if hasattr(spec, 'main'):
                    # Run the main function
                    if asyncio.iscoroutinefunction(spec.main):
                        result = await spec.main()
                    else:
                        result = spec.main()
                    
                    return bool(result)
                else:
                    logger.warning(f"Script {script_name} has no main function")
                    return True
                    
            finally:
                # Restore original directory
                os.chdir(original_dir)
                
        except Exception as e:
            logger.error(f"Failed to run script {script_path}: {str(e)}")
            return False
    
    async def _generate_final_report(self):
        """Generate final migration report"""
        try:
            report = {
                "migration_plan": self.migration_plan,
                "execution_summary": {
                    "total_steps": len(self.migration_steps),
                    "completed_steps": len(self.migration_plan["completed_steps"]),
                    "failed_steps": len(self.migration_plan["failed_steps"]),
                    "success_rate": len(self.migration_plan["completed_steps"]) / len(self.migration_steps) * 100
                },
                "timestamp": datetime.now().isoformat(),
                "recommendations": []
            }
            
            # Generate recommendations
            if self.migration_plan["failed_steps"]:
                report["recommendations"].append("Review and resolve failed migration steps")
            
            if self.migration_plan["overall_status"] == "completed":
                report["recommendations"].append("Begin monitoring system stability for 2-4 weeks")
                report["recommendations"].append("Prepare for legacy system decommissioning")
            
            # Save report
            os.makedirs("reports", exist_ok=True)
            report_filename = f"production_migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_path = os.path.join("reports", report_filename)
            
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"📁 Final migration report saved to: {report_path}")
            
            # Display summary
            self._display_execution_summary(report)
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate final report: {str(e)}")
            return None
    
    def _display_execution_summary(self, report: Dict[str, Any]):
        """Display execution summary"""
        print("\n" + "=" * 60)
        print("🎯 PRODUCTION MIGRATION EXECUTION SUMMARY")
        print("=" * 60)
        
        summary = report["execution_summary"]
        print(f"Total Steps: {summary['total_steps']}")
        print(f"Completed: {summary['completed_steps']}")
        print(f"Failed: {summary['failed_steps']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Overall Status: {self.migration_plan['overall_status'].upper()}")
        
        if report.get("recommendations"):
            print("\n📋 RECOMMENDATIONS:")
            for rec in report["recommendations"]:
                print(f"  • {rec}")
        
        print("\n" + "=" * 60)

async def main():
    """Main execution function"""
    orchestrator = ProductionMigrationOrchestrator()
    
    try:
        success = await orchestrator.execute_migration_plan()
        return success
        
    except Exception as e:
        logger.error(f"Migration orchestration failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
