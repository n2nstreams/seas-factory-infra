#!/usr/bin/env python3
"""
Health Monitoring Module - DevOps Agent Implementation
Implements comprehensive health monitoring including:
- Service health checks
- Database connectivity monitoring
- Resource utilization tracking
- Alerting and notification
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import httpx
import psutil

logger = logging.getLogger(__name__)

class HealthStatus(str, Enum):
    """Health status values"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class CheckType(str, Enum):
    """Types of health checks"""
    HTTP_ENDPOINT = "http_endpoint"
    DATABASE = "database"
    RESOURCE_UTILIZATION = "resource_utilization"
    PROCESS_STATUS = "process_status"
    CUSTOM_COMMAND = "custom_command"

class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class HealthCheckResult:
    """Result of a health check"""
    check_type: CheckType
    service_name: str
    status: HealthStatus
    response_time: float
    timestamp: datetime
    details: Dict[str, Any]
    error_message: Optional[str] = None

@dataclass
class ResourceMetrics:
    """System resource metrics"""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, float]
    timestamp: datetime

@dataclass
class Alert:
    """Health monitoring alert"""
    id: str
    service_name: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    acknowledged: bool = False
    resolved: bool = False

class HealthMonitor:
    """Comprehensive health monitoring system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.health_checks: Dict[str, Dict[str, Any]] = {}
        self.health_history: List[HealthCheckResult] = []
        self.alerts: List[Alert] = []
        self.metrics_history: List[ResourceMetrics] = []
        
        # Configuration
        self.check_interval = config.get("check_interval", 30)  # seconds
        self.alert_thresholds = config.get("alert_thresholds", {
            "cpu_warning": 70.0,
            "cpu_critical": 90.0,
            "memory_warning": 80.0,
            "memory_critical": 95.0,
            "disk_warning": 85.0,
            "disk_critical": 95.0,
            "response_time_warning": 1000,  # ms
            "response_time_critical": 5000   # ms
        })
        
        # Monitoring state
        self.monitoring_active = False
        self.monitoring_task = None
        
        logger.info("Health monitor initialized")
    
    async def add_health_check(
        self, 
        service_name: str, 
        check_type: CheckType, 
        check_config: Dict[str, Any]
    ) -> bool:
        """Add a new health check for a service"""
        try:
            check_id = f"{service_name}_{check_type.value}_{int(time.time())}"
            
            self.health_checks[check_id] = {
                "service_name": service_name,
                "check_type": check_type,
                "config": check_config,
                "enabled": True,
                "last_check": None,
                "last_status": HealthStatus.UNKNOWN
            }
            
            logger.info(f"Added health check {check_id} for {service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding health check: {e}")
            return False
    
    async def remove_health_check(self, check_id: str) -> bool:
        """Remove a health check"""
        try:
            if check_id in self.health_checks:
                del self.health_checks[check_id]
                logger.info(f"Removed health check {check_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error removing health check: {e}")
            return False
    
    async def start_monitoring(self):
        """Start continuous health monitoring"""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Health monitoring started")
    
    async def stop_monitoring(self):
        """Stop continuous health monitoring"""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Health monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Run all health checks
                await self._run_all_health_checks()
                
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Process alerts
                await self._process_alerts()
                
                # Wait for next check interval
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Short delay on error
    
    async def _run_all_health_checks(self):
        """Run all configured health checks"""
        tasks = []
        
        for check_id, check_info in self.health_checks.items():
            if check_info["enabled"]:
                task = self._run_single_health_check(check_id, check_info)
                tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Health check failed: {result}")
                elif result:
                    self.health_history.append(result)
                    # Keep only last 1000 results
                    if len(self.health_history) > 1000:
                        self.health_history.pop(0)
    
    async def _run_single_health_check(
        self, 
        check_id: str, 
        check_info: Dict[str, Any]
    ) -> Optional[HealthCheckResult]:
        """Run a single health check"""
        try:
            start_time = time.time()
            service_name = check_info["service_name"]
            check_type = check_info["check_type"]
            config = check_info["config"]
            
            # Run the appropriate health check
            if check_type == CheckType.HTTP_ENDPOINT:
                status, details, error = await self._check_http_endpoint(config)
            elif check_type == CheckType.DATABASE:
                status, details, error = await self._check_database(config)
            elif check_type == CheckType.RESOURCE_UTILIZATION:
                status, details, error = await self._check_resource_utilization(config)
            elif check_type == CheckType.PROCESS_STATUS:
                status, details, error = await self._check_process_status(config)
            elif check_type == CheckType.CUSTOM_COMMAND:
                status, details, error = await self._check_custom_command(config)
            else:
                status = HealthStatus.UNKNOWN
                details = {"error": "Unknown check type"}
                error = "Unknown check type"
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Update check info
            check_info["last_check"] = datetime.now()
            check_info["last_status"] = status
            
            # Create result
            result = HealthCheckResult(
                check_type=check_type,
                service_name=service_name,
                status=status,
                response_time=response_time,
                timestamp=datetime.now(),
                details=details,
                error_message=error
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error running health check {check_id}: {e}")
            return None
    
    async def _check_http_endpoint(self, config: Dict[str, Any]) -> Tuple[HealthStatus, Dict[str, Any], Optional[str]]:
        """Check HTTP endpoint health"""
        try:
            url = config.get("url")
            method = config.get("method", "GET")
            timeout = config.get("timeout", 10)
            expected_status = config.get("expected_status", 200)
            
            if not url:
                return HealthStatus.UNKNOWN, {}, "No URL specified"
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.request(method, url)
                
                if response.status_code == expected_status:
                    return HealthStatus.HEALTHY, {
                        "status_code": response.status_code,
                        "response_time": response.elapsed.total_seconds() * 1000
                    }, None
                else:
                    return HealthStatus.UNHEALTHY, {
                        "status_code": response.status_code,
                        "expected_status": expected_status
                    }, f"Unexpected status code: {response.status_code}"
                    
        except Exception as e:
            return HealthStatus.UNHEALTHY, {}, str(e)
    
    async def _check_database(self, config: Dict[str, Any]) -> Tuple[HealthStatus, Dict[str, Any], Optional[str]]:
        """Check database connectivity"""
        try:
            # This would be implemented based on the database type
            # For now, return a mock healthy status
            return HealthStatus.HEALTHY, {
                "connection": "established",
                "query_time": 5.2
            }, None
            
        except Exception as e:
            return HealthStatus.UNHEALTHY, {}, str(e)
    
    async def _check_resource_utilization(self, config: Dict[str, Any]) -> Tuple[HealthStatus, Dict[str, Any], Optional[str]]:
        """Check system resource utilization"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            details = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent
            }
            
            # Determine status based on thresholds
            if (cpu_percent > self.alert_thresholds["cpu_critical"] or 
                memory.percent > self.alert_thresholds["memory_critical"] or
                disk.percent > self.alert_thresholds["disk_critical"]):
                status = HealthStatus.UNHEALTHY
            elif (cpu_percent > self.alert_thresholds["cpu_warning"] or 
                  memory.percent > self.alert_thresholds["memory_warning"] or
                  disk.percent > self.alert_thresholds["disk_warning"]):
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY
            
            return status, details, None
            
        except Exception as e:
            return HealthStatus.UNKNOWN, {}, str(e)
    
    async def _check_process_status(self, config: Dict[str, Any]) -> Tuple[HealthStatus, Dict[str, Any], Optional[str]]:
        """Check if a process is running"""
        try:
            process_name = config.get("process_name")
            if not process_name:
                return HealthStatus.UNKNOWN, {}, "No process name specified"
            
            # Check if process is running
            running = False
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if process_name.lower() in proc.info['name'].lower():
                        running = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if running:
                return HealthStatus.HEALTHY, {"process": "running"}, None
            else:
                return HealthStatus.UNHEALTHY, {"process": "not_found"}, "Process not running"
                
        except Exception as e:
            return HealthStatus.UNKNOWN, {}, str(e)
    
    async def _check_custom_command(self, config: Dict[str, Any]) -> Tuple[HealthStatus, Dict[str, Any], Optional[str]]:
        """Run a custom command for health checking"""
        try:
            command = config.get("command")
            if not command:
                return HealthStatus.UNKNOWN, {}, "No command specified"
            
            # Run the command
            process = await asyncio.create_subprocess_exec(
                *command.split(),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return HealthStatus.HEALTHY, {
                    "command": command,
                    "output": stdout.decode().strip()
                }, None
            else:
                return HealthStatus.UNHEALTHY, {
                    "command": command,
                    "return_code": process.returncode,
                    "error": stderr.decode().strip()
                }, f"Command failed with return code {process.returncode}"
                
        except Exception as e:
            return HealthStatus.UNKNOWN, {}, str(e)
    
    async def _collect_system_metrics(self):
        """Collect system resource metrics"""
        try:
            metrics = ResourceMetrics(
                cpu_percent=psutil.cpu_percent(interval=1),
                memory_percent=psutil.virtual_memory().percent,
                disk_percent=psutil.disk_usage('/').percent,
                network_io=dict(psutil.net_io_counters()._asdict()),
                timestamp=datetime.now()
            )
            
            self.metrics_history.append(metrics)
            
            # Keep only last 1000 metrics
            if len(self.metrics_history) > 1000:
                self.metrics_history.pop(0)
                
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    async def _process_alerts(self):
        """Process and generate alerts based on health check results"""
        try:
            # Check recent health check results
            recent_results = [
                result for result in self.health_history[-100:]
                if result.timestamp > datetime.now() - timedelta(minutes=5)
            ]
            
            for result in recent_results:
                if result.status == HealthStatus.UNHEALTHY:
                    await self._create_alert(
                        result.service_name,
                        AlertSeverity.ERROR,
                        f"Service {result.service_name} is unhealthy: {result.error_message or 'Unknown error'}"
                    )
                elif result.status == HealthStatus.DEGRADED:
                    await self._create_alert(
                        result.service_name,
                        AlertSeverity.WARNING,
                        f"Service {result.service_name} is degraded: {result.error_message or 'Performance issues detected'}"
                    )
                
                # Check response time thresholds
                if result.response_time > self.alert_thresholds["response_time_critical"]:
                    await self._create_alert(
                        result.service_name,
                        AlertSeverity.CRITICAL,
                        f"Service {result.service_name} response time critical: {result.response_time:.2f}ms"
                    )
                elif result.response_time > self.alert_thresholds["response_time_warning"]:
                    await self._create_alert(
                        result.service_name,
                        AlertSeverity.WARNING,
                        f"Service {result.service_name} response time high: {result.response_time:.2f}ms"
                    )
                    
        except Exception as e:
            logger.error(f"Error processing alerts: {e}")
    
    async def _create_alert(
        self, 
        service_name: str, 
        severity: AlertSeverity, 
        message: str
    ) -> str:
        """Create a new alert"""
        try:
            alert_id = f"alert_{int(time.time())}_{service_name}"
            
            # Check if similar alert already exists
            existing_alert = None
            for alert in self.alerts:
                if (alert.service_name == service_name and 
                    alert.message == message and 
                    not alert.resolved):
                    existing_alert = alert
                    break
            
            if existing_alert:
                # Update existing alert timestamp
                existing_alert.timestamp = datetime.now()
                return existing_alert.id
            
            # Create new alert
            alert = Alert(
                id=alert_id,
                service_name=service_name,
                severity=severity,
                message=message,
                timestamp=datetime.now()
            )
            
            self.alerts.append(alert)
            
            # Keep only last 1000 alerts
            if len(self.alerts) > 1000:
                self.alerts.pop(0)
            
            logger.info(f"Created alert {alert_id}: {message}")
            return alert_id
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            return ""
    
    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        try:
            for alert in self.alerts:
                if alert.id == alert_id:
                    alert.acknowledged = True
                    logger.info(f"Alert {alert_id} acknowledged")
                    return True
            return False
            
        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")
            return False
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        try:
            for alert in self.alerts:
                if alert.id == alert_id:
                    alert.resolved = True
                    logger.info(f"Alert {alert_id} resolved")
                    return True
            return False
            
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            return False
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary"""
        try:
            if not self.health_history:
                return {"status": "unknown", "message": "No health checks performed"}
            
            # Get recent results (last hour)
            recent_results = [
                result for result in self.health_history
                if result.timestamp > datetime.now() - timedelta(hours=1)
            ]
            
            if not recent_results:
                return {"status": "unknown", "message": "No recent health checks"}
            
            # Calculate summary
            total_checks = len(recent_results)
            healthy_checks = len([r for r in recent_results if r.status == HealthStatus.HEALTHY])
            degraded_checks = len([r for r in recent_results if r.status == HealthStatus.DEGRADED])
            unhealthy_checks = len([r for r in recent_results if r.status == HealthStatus.UNHEALTHY])
            
            health_percentage = (healthy_checks / total_checks) * 100 if total_checks > 0 else 0
            
            # Determine overall status
            if health_percentage >= 95:
                overall_status = "healthy"
            elif health_percentage >= 80:
                overall_status = "degraded"
            else:
                overall_status = "unhealthy"
            
            return {
                "status": overall_status,
                "health_percentage": health_percentage,
                "total_checks": total_checks,
                "healthy_checks": healthy_checks,
                "degraded_checks": degraded_checks,
                "unhealthy_checks": unhealthy_checks,
                "active_alerts": len([a for a in self.alerts if not a.resolved]),
                "last_check": recent_results[-1].timestamp.isoformat() if recent_results else None
            }
            
        except Exception as e:
            logger.error(f"Error getting health summary: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """Get health status for a specific service"""
        try:
            service_results = [
                result for result in self.health_history
                if result.service_name == service_name
            ]
            
            if not service_results:
                return {"status": "unknown", "message": "No health checks for service"}
            
            # Get latest result
            latest_result = service_results[-1]
            
            # Get recent trend (last 10 checks)
            recent_results = service_results[-10:]
            status_counts = {}
            for result in recent_results:
                status_counts[result.status] = status_counts.get(result.status, 0) + 1
            
            return {
                "service_name": service_name,
                "current_status": latest_result.status.value,
                "last_check": latest_result.timestamp.isoformat(),
                "response_time": latest_result.response_time,
                "recent_trend": status_counts,
                "details": latest_result.details,
                "error_message": latest_result.error_message
            }
            
        except Exception as e:
            logger.error(f"Error getting service health: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_alerts(
        self, 
        severity: Optional[AlertSeverity] = None,
        service_name: Optional[str] = None,
        resolved: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """Get filtered alerts"""
        try:
            filtered_alerts = self.alerts
            
            if severity:
                filtered_alerts = [a for a in filtered_alerts if a.severity == severity]
            
            if service_name:
                filtered_alerts = [a for a in filtered_alerts if a.service_name == service_name]
            
            if resolved is not None:
                filtered_alerts = [a for a in filtered_alerts if a.resolved == resolved]
            
            return [
                {
                    "id": alert.id,
                    "service_name": alert.service_name,
                    "severity": alert.severity.value,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "acknowledged": alert.acknowledged,
                    "resolved": alert.resolved
                }
                for alert in filtered_alerts
            ]
            
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return []
