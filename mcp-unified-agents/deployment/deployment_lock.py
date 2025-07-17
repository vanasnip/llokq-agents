"""
Deployment locking mechanism to prevent concurrent deployments
Uses file-based locking with PID and timeout handling
"""
import os
import time
import json
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime, timedelta


class DeploymentLock:
    """Manages deployment locking to prevent concurrent operations"""
    
    def __init__(self, lock_dir: str = "~/.mcp-deployment"):
        self.lock_dir = Path(lock_dir).expanduser()
        self.lock_dir.mkdir(parents=True, exist_ok=True)
        self.lock_file = self.lock_dir / "deployment.lock"
        self.timeout_minutes = 30  # Auto-release after 30 minutes
        self._lock_data = None
    
    def _read_lock(self) -> Optional[Dict]:
        """Read current lock file"""
        if not self.lock_file.exists():
            return None
        
        try:
            with open(self.lock_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # Corrupted lock file, remove it
            self.lock_file.unlink(missing_ok=True)
            return None
    
    def _write_lock(self, data: Dict):
        """Write lock data to file"""
        with open(self.lock_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _is_process_alive(self, pid: int) -> bool:
        """Check if a process with given PID is still running"""
        try:
            # Send signal 0 to check if process exists
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False
    
    def is_locked(self) -> bool:
        """Check if deployment is currently locked"""
        lock_data = self._read_lock()
        
        if not lock_data:
            return False
        
        # Check if lock is expired
        lock_time = datetime.fromisoformat(lock_data['locked_at'])
        if datetime.now() - lock_time > timedelta(minutes=self.timeout_minutes):
            # Lock expired, remove it
            self.force_release()
            return False
        
        # Check if process is still alive
        pid = lock_data.get('pid')
        if pid and not self._is_process_alive(pid):
            # Process died, remove stale lock
            self.force_release()
            return False
        
        return True
    
    def acquire(self, operation: str = "deployment", force: bool = False) -> bool:
        """
        Acquire deployment lock
        
        Args:
            operation: Description of the operation
            force: Force acquire even if locked
            
        Returns:
            True if lock acquired, False otherwise
        """
        if not force and self.is_locked():
            return False
        
        self._lock_data = {
            'pid': os.getpid(),
            'locked_at': datetime.now().isoformat(),
            'operation': operation,
            'hostname': os.uname().nodename,
            'user': os.environ.get('USER', 'unknown')
        }
        
        self._write_lock(self._lock_data)
        return True
    
    def release(self):
        """Release deployment lock"""
        if self.lock_file.exists():
            # Verify we own the lock
            lock_data = self._read_lock()
            if lock_data and lock_data.get('pid') == os.getpid():
                self.lock_file.unlink(missing_ok=True)
                self._lock_data = None
    
    def force_release(self):
        """Force release lock (use with caution)"""
        self.lock_file.unlink(missing_ok=True)
        self._lock_data = None
    
    def get_lock_info(self) -> Optional[Dict]:
        """Get information about current lock"""
        return self._read_lock()
    
    def wait_for_lock(self, timeout_seconds: int = 300) -> bool:
        """
        Wait for lock to become available
        
        Args:
            timeout_seconds: Maximum time to wait
            
        Returns:
            True if lock acquired, False if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            if self.acquire():
                return True
            
            # Wait a bit before trying again
            time.sleep(5)
        
        return False
    
    def __enter__(self):
        """Context manager entry"""
        if not self.acquire():
            lock_info = self.get_lock_info()
            if lock_info:
                raise RuntimeError(
                    f"Deployment already in progress:\n"
                    f"  Started: {lock_info['locked_at']}\n"
                    f"  Operation: {lock_info['operation']}\n"
                    f"  User: {lock_info['user']}@{lock_info['hostname']}\n"
                    f"  PID: {lock_info['pid']}"
                )
            else:
                raise RuntimeError("Failed to acquire deployment lock")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.release()