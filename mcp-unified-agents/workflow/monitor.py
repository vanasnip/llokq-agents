"""
Resource monitoring for workflow execution
"""
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    
import os
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ResourceMonitor:
    """
    Monitors resource usage for workflow execution
    """
    
    def __init__(self, max_memory_mb: int = 512):
        self.max_memory_mb = max_memory_mb
        if PSUTIL_AVAILABLE:
            self.process = psutil.Process(os.getpid())
            self.start_memory = self.get_memory_usage()
        else:
            self.process = None
            self.start_memory = 0
            logger.warning("psutil not available - resource monitoring disabled")
        self.workflow_memory = {}
        
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        if not PSUTIL_AVAILABLE or not self.process:
            return 0
        return self.process.memory_info().rss / 1024 / 1024
        
    def check_memory_limit(self, workflow_id: str) -> bool:
        """Check if workflow is within memory limits"""
        current_memory = self.get_memory_usage()
        workflow_start = self.workflow_memory.get(workflow_id, self.start_memory)
        workflow_usage = current_memory - workflow_start
        
        if workflow_usage > self.max_memory_mb:
            logger.warning(
                f"Workflow {workflow_id} exceeds memory limit: "
                f"{workflow_usage:.1f}MB > {self.max_memory_mb}MB"
            )
            return False
            
        return True
        
    def start_monitoring(self, workflow_id: str):
        """Start monitoring a workflow"""
        self.workflow_memory[workflow_id] = self.get_memory_usage()
        logger.info(f"Started monitoring workflow {workflow_id}")
        
    def stop_monitoring(self, workflow_id: str):
        """Stop monitoring a workflow"""
        if workflow_id in self.workflow_memory:
            del self.workflow_memory[workflow_id]
            logger.info(f"Stopped monitoring workflow {workflow_id}")
            
    def get_stats(self) -> Dict[str, Any]:
        """Get current resource statistics"""
        if not PSUTIL_AVAILABLE or not self.process:
            return {
                "current_memory_mb": 0,
                "start_memory_mb": 0,
                "active_workflows": len(self.workflow_memory),
                "cpu_percent": 0,
                "threads": 0,
                "monitoring_enabled": False
            }
            
        return {
            "current_memory_mb": self.get_memory_usage(),
            "start_memory_mb": self.start_memory,
            "active_workflows": len(self.workflow_memory),
            "cpu_percent": self.process.cpu_percent(),
            "threads": self.process.num_threads(),
            "monitoring_enabled": True
        }