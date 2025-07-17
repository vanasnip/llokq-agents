"""
Version management for deployment system
Tracks deployment history and manages VERSION file
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import subprocess


class VersionManager:
    """Manages version tracking for deployments"""
    
    def __init__(self, prod_path: str):
        self.prod_path = Path(prod_path)
        self.version_file = self.prod_path / "VERSION"
        self.version_data = self._load_version()
    
    def _load_version(self) -> Dict:
        """Load current version data or create default"""
        if self.version_file.exists():
            try:
                with open(self.version_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # Corrupted file, start fresh
                return self._default_version()
        return self._default_version()
    
    def _default_version(self) -> Dict:
        """Create default version structure"""
        return {
            "version": "0.0.0",
            "deployed": None,
            "deployed_from": None,
            "git_commit": None,
            "files_updated": [],
            "deployed_by": "manual",
            "history": []
        }
    
    def get_current_version(self) -> str:
        """Get current deployed version"""
        return self.version_data.get("version", "0.0.0")
    
    def get_next_version(self) -> str:
        """Calculate next version number (simple increment)"""
        current = self.get_current_version()
        parts = current.split('.')
        try:
            # Increment patch version
            parts[2] = str(int(parts[2]) + 1)
            return '.'.join(parts)
        except (IndexError, ValueError):
            # Fallback if version format is invalid
            return "0.0.1"
    
    def get_git_commit(self, dev_path: str) -> Optional[str]:
        """Get current git commit hash from dev path"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=dev_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()[:8]  # Short hash
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
    
    def record_deployment(self, dev_path: str, files_updated: List[str], 
                         deployed_by: str = "mcp") -> Dict:
        """Record a new deployment"""
        # Archive current version to history
        if self.version_data.get("deployed"):
            history_entry = {
                "version": self.version_data["version"],
                "deployed": self.version_data["deployed"],
                "deployed_from": self.version_data["deployed_from"],
                "git_commit": self.version_data["git_commit"],
                "files_updated": self.version_data["files_updated"],
                "deployed_by": self.version_data["deployed_by"]
            }
            self.version_data["history"].insert(0, history_entry)
            # Keep only last 10 deployments in history
            self.version_data["history"] = self.version_data["history"][:10]
        
        # Update with new deployment info
        self.version_data.update({
            "version": self.get_next_version(),
            "deployed": datetime.now().isoformat(),
            "deployed_from": str(dev_path),
            "git_commit": self.get_git_commit(dev_path),
            "files_updated": files_updated,
            "deployed_by": deployed_by
        })
        
        # Save to file
        self.save()
        return self.version_data
    
    def save(self):
        """Save version data to file"""
        self.version_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.version_file, 'w') as f:
            json.dump(self.version_data, f, indent=2)
    
    def get_deployment_history(self) -> List[Dict]:
        """Get deployment history"""
        history = self.version_data.get("history", [])
        # Include current version as first entry
        if self.version_data.get("deployed"):
            current = {
                "version": self.version_data["version"],
                "deployed": self.version_data["deployed"],
                "deployed_from": self.version_data["deployed_from"],
                "git_commit": self.version_data["git_commit"],
                "files_updated": self.version_data["files_updated"],
                "deployed_by": self.version_data["deployed_by"]
            }
            return [current] + history
        return history
    
    def get_last_deployment(self) -> Optional[Dict]:
        """Get info about the last deployment"""
        if self.version_data.get("deployed"):
            return {
                "version": self.version_data["version"],
                "deployed": self.version_data["deployed"],
                "deployed_from": self.version_data["deployed_from"],
                "git_commit": self.version_data["git_commit"],
                "files_updated": self.version_data["files_updated"],
                "deployed_by": self.version_data["deployed_by"]
            }
        return None