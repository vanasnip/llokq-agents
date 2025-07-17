"""
Main deployment manager for MCP Unified Agents
Handles the deployment process from dev to production
"""
import os
import shutil
import json
import glob
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import filecmp
import logging

from .version_manager import VersionManager
from .deployment_lock import DeploymentLock


class DeploymentManager:
    """Manages deployment from development to production"""
    
    # Files and patterns to sync
    SYNC_PATTERNS = [
        "server.py",
        "agents.json",
        "workflow/*.py",
        "templates/*.json",
        "deployment/*.py"  # Include deployment system itself
    ]
    
    # Files to explicitly exclude
    EXCLUDE_PATTERNS = [
        "*.pyc",
        "__pycache__",
        ".env",
        "*.log",
        "*.tmp",
        ".git",
        ".DS_Store",
        "VERSION",  # Managed separately
        "test_*",   # Test files
        "*.bak"     # Backup files
    ]
    
    def __init__(self, dev_path: str, prod_path: str, backup_dir: str = "~/.mcp-backups/unified-agents"):
        self.dev_path = Path(dev_path).resolve()
        self.prod_path = Path(prod_path).expanduser().resolve()
        self.backup_dir = Path(backup_dir).expanduser()
        
        # Initialize components
        self.version_mgr = VersionManager(self.prod_path)
        self.lock = DeploymentLock()
        self.logger = self._setup_logging()
        
        # Deployment state
        self.dry_run = False
        self.files_to_update = []
        self.backup_path = None
    
    def _setup_logging(self) -> logging.Logger:
        """Setup deployment logging"""
        log_dir = Path("~/.mcp-deployment").expanduser()
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logger = logging.getLogger("deployment")
        logger.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler(log_dir / "deployments.log")
        fh.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(fh)
        
        return logger
    
    def _should_exclude(self, file_path: str) -> bool:
        """Check if file should be excluded from sync"""
        for pattern in self.EXCLUDE_PATTERNS:
            if Path(file_path).match(pattern):
                return True
        return False
    
    def _get_files_to_sync(self) -> List[Tuple[Path, Path]]:
        """Get list of files that need syncing"""
        files_to_sync = []
        
        for pattern in self.SYNC_PATTERNS:
            # Handle both direct files and glob patterns
            if '*' in pattern:
                # It's a glob pattern
                full_pattern = self.dev_path / pattern
                for dev_file in glob.glob(str(full_pattern), recursive=True):
                    dev_file = Path(dev_file)
                    if dev_file.is_file() and not self._should_exclude(str(dev_file)):
                        rel_path = dev_file.relative_to(self.dev_path)
                        prod_file = self.prod_path / rel_path
                        files_to_sync.append((dev_file, prod_file))
            else:
                # Direct file
                dev_file = self.dev_path / pattern
                if dev_file.exists() and dev_file.is_file():
                    prod_file = self.prod_path / pattern
                    files_to_sync.append((dev_file, prod_file))
        
        return files_to_sync
    
    def _file_needs_update(self, dev_file: Path, prod_file: Path) -> bool:
        """Check if a file needs updating"""
        if not prod_file.exists():
            return True
        
        # Compare file contents using hash
        return self._calculate_hash(dev_file) != self._calculate_hash(prod_file)
    
    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def check_changes(self) -> List[Dict]:
        """Check what files would be updated"""
        changes = []
        
        for dev_file, prod_file in self._get_files_to_sync():
            if self._file_needs_update(dev_file, prod_file):
                change_info = {
                    'file': str(dev_file.relative_to(self.dev_path)),
                    'action': 'create' if not prod_file.exists() else 'update',
                    'dev_path': str(dev_file),
                    'prod_path': str(prod_file)
                }
                changes.append(change_info)
        
        return changes
    
    def create_backup(self) -> Path:
        """Create timestamped backup of production"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version = self.version_mgr.get_current_version()
        backup_path = self.backup_dir / f"v{version}_{timestamp}"
        
        self.logger.info(f"Creating backup at {backup_path}")
        
        # Create backup directory
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Copy all files that will be modified
        for change in self.files_to_update:
            if change['action'] == 'update':  # Only backup existing files
                prod_file = Path(change['prod_path'])
                if prod_file.exists():
                    rel_path = prod_file.relative_to(self.prod_path)
                    backup_file = backup_path / rel_path
                    backup_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(prod_file, backup_file)
        
        # Also backup VERSION file if it exists
        version_file = self.prod_path / "VERSION"
        if version_file.exists():
            shutil.copy2(version_file, backup_path / "VERSION")
        
        self.logger.info(f"Backup completed: {backup_path}")
        return backup_path
    
    def sync_files(self):
        """Sync files from dev to production"""
        updated_files = []
        
        for change in self.files_to_update:
            dev_file = Path(change['dev_path'])
            prod_file = Path(change['prod_path'])
            
            self.logger.info(f"Syncing {change['file']} ({change['action']})")
            
            if not self.dry_run:
                # Ensure directory exists
                prod_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file with metadata preserved
                shutil.copy2(dev_file, prod_file)
                
                # Preserve execute permissions for .py files
                if dev_file.suffix == '.py' and os.access(dev_file, os.X_OK):
                    os.chmod(prod_file, os.stat(dev_file).st_mode)
            
            updated_files.append(change['file'])
        
        return updated_files
    
    def run_tests(self) -> bool:
        """Run basic tests to verify deployment"""
        self.logger.info("Running post-deployment tests")
        
        if self.dry_run:
            self.logger.info("Skipping tests in dry-run mode")
            return True
        
        # Test 1: Check Python syntax of deployed files
        for py_file in self.prod_path.glob("**/*.py"):
            if not self._should_exclude(str(py_file)):
                try:
                    with open(py_file, 'r') as f:
                        compile(f.read(), str(py_file), 'exec')
                except SyntaxError as e:
                    self.logger.error(f"Syntax error in {py_file}: {e}")
                    return False
        
        # Test 2: Validate JSON files
        for json_file in [self.prod_path / "agents.json"]:
            if json_file.exists():
                try:
                    with open(json_file, 'r') as f:
                        json.load(f)
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON error in {json_file}: {e}")
                    return False
        
        # Test 3: Try to import the server module
        try:
            import sys
            sys.path.insert(0, str(self.prod_path))
            import importlib.util
            spec = importlib.util.spec_from_file_location("server", self.prod_path / "server.py")
            if spec and spec.loader:
                server = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(server)
            sys.path.pop(0)
        except Exception as e:
            self.logger.error(f"Failed to import server module: {e}")
            return False
        
        self.logger.info("All tests passed")
        return True
    
    def rollback(self, backup_path: Optional[Path] = None):
        """Rollback to a previous version"""
        if not backup_path:
            # Use the most recent backup
            backups = sorted(self.backup_dir.glob("v*_*"), reverse=True)
            if not backups:
                raise RuntimeError("No backups available for rollback")
            backup_path = backups[0]
        
        self.logger.info(f"Rolling back to {backup_path}")
        
        # Restore files from backup
        for backup_file in backup_path.rglob("*"):
            if backup_file.is_file():
                rel_path = backup_file.relative_to(backup_path)
                prod_file = self.prod_path / rel_path
                
                self.logger.info(f"Restoring {rel_path}")
                prod_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup_file, prod_file)
        
        self.logger.info("Rollback completed")
    
    def deploy(self, dry_run: bool = False) -> Dict:
        """
        Main deployment method
        
        Args:
            dry_run: If True, only show what would be done
            
        Returns:
            Deployment result dictionary
        """
        self.dry_run = dry_run
        deployment_result = {
            'success': False,
            'version': None,
            'files_updated': [],
            'error': None,
            'dry_run': dry_run
        }
        
        try:
            with self.lock:
                self.logger.info(f"Starting deployment (dry_run={dry_run})")
                
                # Step 1: Check for changes
                self.files_to_update = self.check_changes()
                
                if not self.files_to_update:
                    deployment_result['success'] = True
                    deployment_result['message'] = "No changes to deploy"
                    return deployment_result
                
                # Step 2: Create backup (skip in dry-run)
                if not dry_run:
                    self.backup_path = self.create_backup()
                
                # Step 3: Sync files
                updated_files = self.sync_files()
                
                # Step 4: Run tests
                if self.run_tests():
                    # Step 5: Update version
                    if not dry_run:
                        version_info = self.version_mgr.record_deployment(
                            self.dev_path,
                            updated_files,
                            "mcp"
                        )
                        deployment_result['version'] = version_info['version']
                    
                    deployment_result['success'] = True
                    deployment_result['files_updated'] = updated_files
                    
                    self.logger.info(f"Deployment successful: {len(updated_files)} files updated")
                else:
                    # Tests failed, rollback
                    if not dry_run and self.backup_path:
                        self.logger.error("Tests failed, rolling back")
                        self.rollback(self.backup_path)
                    deployment_result['error'] = "Post-deployment tests failed"
                
        except Exception as e:
            self.logger.error(f"Deployment failed: {e}")
            deployment_result['error'] = str(e)
            
            # Attempt rollback on failure
            if not dry_run and self.backup_path and self.backup_path.exists():
                try:
                    self.rollback(self.backup_path)
                except Exception as rb_error:
                    self.logger.error(f"Rollback failed: {rb_error}")
        
        return deployment_result
    
    def get_status(self) -> Dict:
        """Get current deployment status"""
        status = {
            'current_version': self.version_mgr.get_current_version(),
            'last_deployment': self.version_mgr.get_last_deployment(),
            'pending_changes': self.check_changes(),
            'is_locked': self.lock.is_locked(),
            'lock_info': self.lock.get_lock_info()
        }
        return status