#!/usr/bin/env python3
"""
Cloud Build Integration for ReviewAgent
Handles Cloud Build API calls and build monitoring
"""

import asyncio
import json
import os
import tempfile
import zipfile
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

try:
    from google.cloud import build_v1
    from google.cloud import storage
    from google.cloud import logging as cloud_logging
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    logging.warning("Google Cloud libraries not available, Cloud Build integration disabled")

logger = logging.getLogger(__name__)

class CloudBuildManager:
    """Manages Google Cloud Build operations for pytest execution"""
    
    def __init__(self):
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "saas-factory-prod")
        self.region = os.getenv("CLOUD_BUILD_REGION", "us-central1")
        self.bucket_name = f"{self.project_id}-build-source"
        
        if GOOGLE_CLOUD_AVAILABLE:
            self.build_client = build_v1.CloudBuildClient()
            self.storage_client = storage.Client()
            self.logging_client = cloud_logging.Client()
        else:
            self.build_client = None
            self.storage_client = None
            self.logging_client = None
    
    def create_source_archive(self, workspace_dir: str) -> str:
        """Create a source archive for Cloud Build"""
        archive_path = tempfile.mktemp(suffix='.zip')
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            workspace_path = Path(workspace_dir)
            
            for file_path in workspace_path.rglob('*'):
                if file_path.is_file():
                    # Skip hidden files and __pycache__
                    if not any(part.startswith('.') or part == '__pycache__' for part in file_path.parts):
                        arcname = file_path.relative_to(workspace_path)
                        zip_file.write(file_path, arcname)
        
        logger.info(f"Created source archive: {archive_path}")
        return archive_path
    
    async def upload_source_to_gcs(self, archive_path: str) -> str:
        """Upload source archive to Google Cloud Storage"""
        if not self.storage_client:
            raise Exception("Google Cloud Storage client not available")
        
        # Create bucket if it doesn't exist
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            if not bucket.exists():
                bucket = self.storage_client.create_bucket(self.bucket_name, location="us")
                logger.info(f"Created bucket: {self.bucket_name}")
        except Exception as e:
            logger.warning(f"Error checking/creating bucket: {e}")
            bucket = self.storage_client.bucket(self.bucket_name)
        
        # Upload archive
        blob_name = f"source/{Path(archive_path).name}"
        blob = bucket.blob(blob_name)
        
        # Upload in a separate thread to avoid blocking
        await asyncio.get_event_loop().run_in_executor(
            None, blob.upload_from_filename, archive_path
        )
        
        gcs_url = f"gs://{self.bucket_name}/{blob_name}"
        logger.info(f"Uploaded source to: {gcs_url}")
        return gcs_url
    
    def create_build_config(self, source_url: str, build_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create Cloud Build configuration"""
        config = {
            "source": {
                "storage_source": {
                    "bucket": self.bucket_name,
                    "object": source_url.replace(f"gs://{self.bucket_name}/", "")
                }
            },
            "steps": [
                {
                    "name": "python:3.11-slim",
                    "entrypoint": "bash",
                    "args": [
                        "-c",
                        """
                        apt-get update && apt-get install -y git curl
                        pip install --upgrade pip
                        pip install pytest pytest-cov pytest-xdist pytest-html pytest-json-report
                        pip install fastapi pydantic asyncpg httpx uvicorn
                        pip install -r requirements.txt || echo "No requirements.txt found"
                        """
                    ]
                },
                {
                    "name": "python:3.11-slim",
                    "entrypoint": "bash",
                    "args": [
                        "-c",
                        """
                        cd /workspace
                        export PYTHONPATH=/workspace/src:$PYTHONPATH
                        echo "Running syntax checks..."
                        find /workspace -name "*.py" -exec python -m py_compile {} \\; || echo "Syntax check failed"
                        """
                    ]
                },
                {
                    "name": "python:3.11-slim",
                    "entrypoint": "bash",
                    "args": [
                        "-c",
                        """
                        cd /workspace
                        export PYTHONPATH=/workspace/src:$PYTHONPATH
                        echo "Starting pytest execution..."
                        
                        python -m pytest \\
                          --tb=short \\
                          --cov=src \\
                          --cov-report=xml:/workspace/coverage.xml \\
                          --cov-report=term-missing \\
                          --junit-xml=/workspace/test-results.xml \\
                          --json-report --json-report-file=/workspace/test-report.json \\
                          -v \\
                          --maxfail=10 \\
                          tests/ > /workspace/pytest-output.log 2>&1 || echo "Tests completed with failures"
                        
                        echo "Test execution completed"
                        echo "Generated artifacts:"
                        ls -la *.xml *.json *.log 2>/dev/null || echo "No artifacts found"
                        """
                    ]
                }
            ],
            "artifacts": {
                "objects": {
                    "location": f"gs://{self.bucket_name}/artifacts/$BUILD_ID",
                    "paths": [
                        "test-results.xml",
                        "coverage.xml", 
                        "test-report.json",
                        "pytest-output.log"
                    ]
                }
            },
            "options": {
                "logging": "CLOUD_LOGGING_ONLY",
                "machine_type": "E2_MEDIUM",
                "disk_size_gb": 20
            },
            "timeout": "600s"
        }
        
        # Merge custom build options
        if build_options:
            config.update(build_options)
        
        return config
    
    async def submit_build(self, build_config: Dict[str, Any]) -> str:
        """Submit build to Cloud Build"""
        if not self.build_client:
            raise Exception("Cloud Build client not available")
        
        try:
            # Submit build in executor to avoid blocking
            operation = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.build_client.create_build(
                    project_id=self.project_id,
                    build=build_config
                )
            )
            
            build_id = operation.metadata.build.id
            logger.info(f"Submitted Cloud Build: {build_id}")
            return build_id
            
        except Exception as e:
            logger.error(f"Error submitting build: {e}")
            raise
    
    async def wait_for_build_completion(self, build_id: str, timeout: int = 600) -> Dict[str, Any]:
        """Wait for build completion and return results"""
        if not self.build_client:
            raise Exception("Cloud Build client not available")
        
        start_time = asyncio.get_event_loop().time()
        
        while True:
            # Check if timeout exceeded
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise Exception(f"Build {build_id} timed out after {timeout} seconds")
            
            try:
                # Get build status in executor
                build = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.build_client.get_build(
                        project_id=self.project_id,
                        id=build_id
                    )
                )
                
                status = build.status.name
                logger.info(f"Build {build_id} status: {status}")
                
                if status in ["SUCCESS", "FAILURE", "TIMEOUT", "CANCELLED"]:
                    # Build completed
                    result = {
                        "build_id": build_id,
                        "status": status.lower(),
                        "duration": (build.finish_time.timestamp() - build.start_time.timestamp()) if build.finish_time and build.start_time else 0,
                        "log_url": build.log_url,
                        "source_provenance": build.source_provenance,
                        "artifacts": []
                    }
                    
                    # Get artifact URLs if available
                    if build.artifacts and build.artifacts.objects:
                        artifact_location = build.artifacts.objects.location
                        for path in build.artifacts.objects.paths:
                            result["artifacts"].append(f"{artifact_location}/{path}")
                    
                    return result
                
                # Wait before checking again
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Error checking build status: {e}")
                await asyncio.sleep(5)
    
    async def download_artifacts(self, artifact_urls: List[str], destination_dir: str) -> Dict[str, str]:
        """Download build artifacts from GCS"""
        if not self.storage_client:
            raise Exception("Google Cloud Storage client not available")
        
        downloaded_files = {}
        destination_path = Path(destination_dir)
        destination_path.mkdir(parents=True, exist_ok=True)
        
        for url in artifact_urls:
            try:
                # Parse GCS URL
                if not url.startswith("gs://"):
                    continue
                
                # Extract bucket and object name
                url_parts = url[5:].split("/", 1)
                if len(url_parts) != 2:
                    continue
                
                bucket_name, object_name = url_parts
                filename = Path(object_name).name
                local_path = destination_path / filename
                
                # Download file in executor
                bucket = self.storage_client.bucket(bucket_name)
                blob = bucket.blob(object_name)
                
                await asyncio.get_event_loop().run_in_executor(
                    None, blob.download_to_filename, str(local_path)
                )
                
                downloaded_files[filename] = str(local_path)
                logger.info(f"Downloaded artifact: {filename}")
                
            except Exception as e:
                logger.error(f"Error downloading artifact {url}: {e}")
        
        return downloaded_files
    
    async def get_build_logs(self, build_id: str) -> str:
        """Get build logs from Cloud Logging"""
        if not self.logging_client:
            return "Cloud Logging not available"
        
        try:
            # Query for build logs
            filter_str = f'resource.type="build" AND resource.labels.build_id="{build_id}"'
            
            entries = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: list(self.logging_client.list_entries(filter_=filter_str, order_by="timestamp desc", max_results=100))
            )
            
            logs = []
            for entry in entries:
                logs.append(f"[{entry.timestamp}] {entry.payload}")
            
            return "\n".join(logs)
            
        except Exception as e:
            logger.error(f"Error fetching build logs: {e}")
            return f"Error fetching logs: {e}"
    
    async def execute_build(self, workspace_dir: str, build_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute complete build process"""
        if not GOOGLE_CLOUD_AVAILABLE:
            raise Exception("Google Cloud libraries not available")
        
        try:
            # Create and upload source
            archive_path = self.create_source_archive(workspace_dir)
            source_url = await self.upload_source_to_gcs(archive_path)
            
            # Create and submit build
            build_config = self.create_build_config(source_url, build_options)
            build_id = await self.submit_build(build_config)
            
            # Wait for completion
            result = await self.wait_for_build_completion(build_id)
            
            # Download artifacts if build succeeded
            if result["status"] == "success" and result["artifacts"]:
                artifacts_dir = tempfile.mkdtemp(prefix="build_artifacts_")
                downloaded_files = await self.download_artifacts(result["artifacts"], artifacts_dir)
                result["downloaded_artifacts"] = downloaded_files
            
            # Get build logs
            result["logs"] = await self.get_build_logs(build_id)
            
            return result
            
        except Exception as e:
            logger.error(f"Build execution failed: {e}")
            raise
        finally:
            # Cleanup source archive
            try:
                os.unlink(archive_path)
            except:
                pass

# Factory function for creating CloudBuildManager
def create_cloud_build_manager() -> Optional[CloudBuildManager]:
    """Create CloudBuildManager if Google Cloud is available"""
    if GOOGLE_CLOUD_AVAILABLE:
        return CloudBuildManager()
    else:
        logger.warning("Google Cloud Build integration not available")
        return None 