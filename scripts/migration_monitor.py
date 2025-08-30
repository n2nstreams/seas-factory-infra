#!/usr/bin/env python3
"""
Migration Progress Monitor
Real-time monitoring of the final data migration process
"""

import os
import sys
import time
import json
import logging
import asyncio
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MigrationMonitor:
    """Real-time monitoring of migration progress and system health"""
    
    def __init__(self):
        self.settings = get_settings()
        self.monitoring_data = {
            "started_at": datetime.now().isoformat(),
            "last_update": None,
            "migration_progress": {},
            "system_health": {},
            "alerts": [],
            "metrics": {
                "total_checks": 0,
                "successful_checks": 0,
                "failed_checks": 0,
                "alert_count": 0
            }
        }
        
        # Monitoring endpoints
        self.api_gateway_url = "http://localhost:8000"
        self.monitoring_interval = 30  # seconds
        
        # Alert thresholds
        self.alert_thresholds = {
            "error_rate": 0.05,  # 5%
            "response_time": 2000,  # 2 seconds
            "migration_drift": 0.01,  # 1%
            "system_health": 0.90  # 90%
        }
    
    async def start_monitoring(self):
        """Start the monitoring process"""
        logger.info("🚀 Starting Migration Progress Monitor")
        logger.info("=" * 50)
        
        try:
            while True:
                # Update monitoring data
                await self._update_monitoring_data()
                
                # Check system health
                await self._check_system_health()
                
                # Check migration progress
                await self._check_migration_progress()
                
                # Generate alerts
                await self._generate_alerts()
                
                # Display status
                self._display_status()
                
                # Save monitoring data
                await self._save_monitoring_data()
                
                # Wait for next check
                await asyncio.sleep(self.monitoring_interval)
                
        except KeyboardInterrupt:
            logger.info("🛑 Monitoring stopped by user")
        except Exception as e:
            logger.error(f"❌ Monitoring failed: {str(e)}")
    
    async def _update_monitoring_data(self):
        """Update monitoring data timestamp"""
        self.monitoring_data["last_update"] = datetime.now().isoformat()
        self.monitoring_data["metrics"]["total_checks"] += 1
    
    async def _check_system_health(self):
        """Check overall system health"""
        try:
            logger.info("🔍 Checking system health...")
            
            health_checks = {
                "api_gateway": await self._check_api_gateway_health(),
                "database_connections": await self._check_database_health(),
                "feature_flags": await self._check_feature_flags_health(),
                "migration_controllers": await self._check_migration_controllers()
            }
            
            # Calculate overall health score
            health_scores = [score for score in health_checks.values() if score is not None]
            overall_health = sum(health_scores) / len(health_scores) if health_scores else 0
            
            self.monitoring_data["system_health"] = {
                "overall_score": overall_health,
                "components": health_checks,
                "timestamp": datetime.now().isoformat()
            }
            
            self.monitoring_data["metrics"]["successful_checks"] += 1
            
        except Exception as e:
            logger.error(f"System health check failed: {str(e)}")
            self.monitoring_data["metrics"]["failed_checks"] += 1
    
    async def _check_api_gateway_health(self) -> float:
        """Check API gateway health"""
        try:
            response = requests.get(f"{self.api_gateway_url}/health", timeout=5)
            if response.status_code == 200:
                return 100.0
            else:
                return 50.0
        except Exception as e:
            logger.error(f"API gateway health check failed: {str(e)}")
            return 0.0
    
    async def _check_database_health(self) -> float:
        """Check database connection health"""
        try:
            # Check legacy database
            legacy_healthy = await self._test_database_connection(
                self.settings.DB_HOST,
                self.settings.DB_PORT,
                self.settings.DB_NAME,
                self.settings.DB_USER,
                self.settings.DB_PASSWORD
            )
            
            # Check Supabase
            supabase_healthy = await self._test_database_connection(
                self.settings.SUPABASE_HOST,
                self.settings.SUPABASE_PORT,
                self.settings.SUPABASE_DB_NAME,
                self.settings.SUPABASE_USER,
                self.settings.SUPABASE_PASSWORD
            )
            
            # Return average health score
            scores = [100.0 if legacy_healthy else 0.0, 100.0 if supabase_healthy else 0.0]
            return sum(scores) / len(scores)
            
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return 0.0
    
    async def _test_database_connection(self, host: str, port: int, database: str, user: str, password: str) -> bool:
        """Test database connection"""
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
                connect_timeout=5
            )
            conn.close()
            return True
        except Exception:
            return False
    
    async def _check_feature_flags_health(self) -> float:
        """Check feature flags system health"""
        try:
            response = requests.get(f"{self.api_gateway_url}/api/feature-flags/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if "flags" in data and len(data["flags"]) > 0:
                    return 100.0
                else:
                    return 50.0
            else:
                return 0.0
        except Exception as e:
            logger.error(f"Feature flags health check failed: {str(e)}")
            return 0.0
    
    async def _check_migration_controllers(self) -> float:
        """Check migration controller endpoints"""
        try:
            endpoints = [
                "/api/monitoring/health",
                "/api/notifications/status"
            ]
            
            healthy_endpoints = 0
            for endpoint in endpoints:
                try:
                    response = requests.get(f"{self.api_gateway_url}{endpoint}", timeout=5)
                    if response.status_code == 200:
                        healthy_endpoints += 1
                except Exception:
                    pass
            
            return (healthy_endpoints / len(endpoints)) * 100
            
        except Exception as e:
            logger.error(f"Migration controllers health check failed: {str(e)}")
            return 0.0
    
    async def _check_migration_progress(self):
        """Check migration progress from database"""
        try:
            logger.info("📊 Checking migration progress...")
            
            # Try to get migration progress from Supabase
            migration_progress = await self._get_migration_progress()
            
            if migration_progress:
                self.monitoring_data["migration_progress"] = migration_progress
                logger.info(f"Migration progress: {migration_progress.get('tables_completed', 0)}/{migration_progress.get('total_tables', 0)}")
            else:
                logger.info("No migration progress data available")
                
        except Exception as e:
            logger.error(f"Migration progress check failed: {str(e)}")
    
    async def _get_migration_progress(self) -> Optional[Dict[str, Any]]:
        """Get migration progress from database"""
        try:
            conn = psycopg2.connect(
                host=self.settings.SUPABASE_HOST,
                port=self.settings.SUPABASE_PORT,
                database=self.settings.SUPABASE_DB_NAME,
                user=self.settings.SUPABASE_USER,
                password=self.settings.SUPABASE_PASSWORD
            )
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get migration status
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_tables,
                        COUNT(CASE WHEN status = 'completed' THEN 1 END) as tables_completed,
                        COUNT(CASE WHEN status = 'failed' THEN 1 END) as tables_failed,
                        COUNT(CASE WHEN status = 'pending' THEN 1 END) as tables_pending
                    FROM cutover_tables
                """)
                
                result = cursor.fetchone()
                if result:
                    return {
                        "total_tables": result["total_tables"],
                        "tables_completed": result["tables_completed"],
                        "tables_failed": result["tables_failed"],
                        "tables_pending": result["tables_pending"],
                        "completion_percentage": (result["tables_completed"] / result["total_tables"] * 100) if result["total_tables"] > 0 else 0
                    }
            
            conn.close()
            return None
            
        except Exception as e:
            logger.error(f"Failed to get migration progress: {str(e)}")
            return None
    
    async def _generate_alerts(self):
        """Generate alerts based on thresholds"""
        try:
            current_alerts = []
            
            # Check system health
            overall_health = self.monitoring_data["system_health"].get("overall_score", 0)
            if overall_health < (self.alert_thresholds["system_health"] * 100):
                current_alerts.append({
                    "level": "CRITICAL",
                    "message": f"System health below threshold: {overall_health:.1f}/100",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Check migration progress
            migration_progress = self.monitoring_data.get("migration_progress", {})
            if migration_progress:
                failed_tables = migration_progress.get("tables_failed", 0)
                if failed_tables > 0:
                    current_alerts.append({
                        "level": "WARNING",
                        "message": f"{failed_tables} migration tables failed",
                        "timestamp": datetime.now().isoformat()
                    })
            
            # Add new alerts
            for alert in current_alerts:
                if alert not in self.monitoring_data["alerts"]:
                    self.monitoring_data["alerts"].append(alert)
                    self.monitoring_data["metrics"]["alert_count"] += 1
                    logger.warning(f"🚨 ALERT: {alert['message']}")
            
        except Exception as e:
            logger.error(f"Alert generation failed: {str(e)}")
    
    def _display_status(self):
        """Display current monitoring status"""
        try:
            # Clear screen (works on most terminals)
            os.system('clear' if os.name == 'posix' else 'cls')
            
            print("🚀 MIGRATION PROGRESS MONITOR")
            print("=" * 50)
            print(f"Started: {self.monitoring_data['started_at']}")
            print(f"Last Update: {self.monitoring_data['last_update']}")
            print(f"Total Checks: {self.monitoring_data['metrics']['total_checks']}")
            print(f"Success Rate: {(self.monitoring_data['metrics']['successful_checks'] / self.monitoring_data['metrics']['total_checks'] * 100):.1f}%")
            print()
            
            # System Health
            system_health = self.monitoring_data.get("system_health", {})
            if system_health:
                print("🔍 SYSTEM HEALTH")
                print(f"Overall Score: {system_health.get('overall_score', 0):.1f}/100")
                components = system_health.get("components", {})
                for component, score in components.items():
                    if score is not None:
                        status = "✅" if score >= 90 else "⚠️" if score >= 70 else "❌"
                        print(f"  {status} {component}: {score:.1f}/100")
                print()
            
            # Migration Progress
            migration_progress = self.monitoring_data.get("migration_progress", {})
            if migration_progress:
                print("📊 MIGRATION PROGRESS")
                print(f"Tables Completed: {migration_progress.get('tables_completed', 0)}/{migration_progress.get('total_tables', 0)}")
                print(f"Completion: {migration_progress.get('completion_percentage', 0):.1f}%")
                print(f"Failed Tables: {migration_progress.get('tables_failed', 0)}")
                print(f"Pending Tables: {migration_progress.get('tables_pending', 0)}")
                print()
            
            # Alerts
            alerts = self.monitoring_data.get("alerts", [])
            if alerts:
                print("🚨 ACTIVE ALERTS")
                for alert in alerts[-5:]:  # Show last 5 alerts
                    level_icon = "🔴" if alert["level"] == "CRITICAL" else "🟡"
                    print(f"  {level_icon} {alert['level']}: {alert['message']}")
                print()
            
            print("Press Ctrl+C to stop monitoring...")
            
        except Exception as e:
            logger.error(f"Status display failed: {str(e)}")
    
    async def _save_monitoring_data(self):
        """Save monitoring data to file"""
        try:
            os.makedirs("reports", exist_ok=True)
            
            filename = f"migration_monitoring_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join("reports", filename)
            
            with open(filepath, 'w') as f:
                json.dump(self.monitoring_data, f, indent=2, default=str)
            
            # Keep only recent files
            await self._cleanup_old_reports()
            
        except Exception as e:
            logger.error(f"Failed to save monitoring data: {str(e)}")
    
    async def _cleanup_old_reports(self):
        """Clean up old monitoring reports"""
        try:
            reports_dir = "reports"
            if not os.path.exists(reports_dir):
                return
            
            # Keep only last 10 monitoring files
            files = [f for f in os.listdir(reports_dir) if f.startswith("migration_monitoring_")]
            files.sort(reverse=True)
            
            for old_file in files[10:]:
                try:
                    os.remove(os.path.join(reports_dir, old_file))
                except Exception:
                    pass
                    
        except Exception as e:
            logger.error(f"Failed to cleanup old reports: {str(e)}")

async def main():
    """Main function"""
    monitor = MigrationMonitor()
    
    try:
        await monitor.start_monitoring()
    except Exception as e:
        logger.error(f"Monitoring failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
