"""
Schema Versioning - Handles configuration schema versions and migrations
"""
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from datetime import datetime
import yaml
import json
from pathlib import Path
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class SchemaType(Enum):
    """Types of schemas in the system"""
    AGENT = "agent"
    PHASE = "phase"
    WORKFLOW = "workflow"
    CONFIG = "config"


@dataclass
class SchemaVersion:
    """Represents a schema version"""
    major: int
    minor: int
    patch: int
    
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
    
    @classmethod
    def from_string(cls, version_str: str) -> "SchemaVersion":
        """Parse version from string like '1.2.3'"""
        parts = version_str.split('.')
        if len(parts) != 3:
            raise ValueError(f"Invalid version format: {version_str}")
        return cls(
            major=int(parts[0]),
            minor=int(parts[1]),
            patch=int(parts[2])
        )
    
    def __lt__(self, other: "SchemaVersion") -> bool:
        """Compare versions for ordering"""
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
    
    def __eq__(self, other: "SchemaVersion") -> bool:
        """Check version equality"""
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)


class SchemaMigration:
    """Base class for schema migrations"""
    
    def __init__(self, from_version: SchemaVersion, to_version: SchemaVersion):
        self.from_version = from_version
        self.to_version = to_version
    
    def migrate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply migration to data"""
        raise NotImplementedError("Subclasses must implement migrate()")
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate data can be migrated"""
        return True


class SchemaValidator:
    """Validates and migrates configuration schemas"""
    
    # Current schema versions
    CURRENT_VERSIONS = {
        SchemaType.AGENT: SchemaVersion(1, 1, 0),
        SchemaType.PHASE: SchemaVersion(1, 0, 0),
        SchemaType.WORKFLOW: SchemaVersion(1, 0, 0),
        SchemaType.CONFIG: SchemaVersion(1, 0, 0)
    }
    
    def __init__(self):
        self.migrations: Dict[SchemaType, List[SchemaMigration]] = {
            schema_type: [] for schema_type in SchemaType
        }
        self._register_builtin_migrations()
    
    def _register_builtin_migrations(self) -> None:
        """Register built-in schema migrations"""
        # Agent schema migrations
        self.register_migration(
            SchemaType.AGENT,
            AgentSchema_1_0_to_1_1()
        )
    
    def register_migration(self, schema_type: SchemaType, migration: SchemaMigration) -> None:
        """Register a migration for a schema type"""
        self.migrations[schema_type].append(migration)
        # Keep migrations sorted by from_version
        self.migrations[schema_type].sort(key=lambda m: m.from_version)
    
    def validate_and_migrate(self, data: Dict[str, Any], schema_type: SchemaType) -> Dict[str, Any]:
        """Validate and migrate data to current schema version"""
        # Get version from data
        version_str = data.get('schema_version', '1.0.0')
        version = SchemaVersion.from_string(version_str)
        
        current_version = self.CURRENT_VERSIONS[schema_type]
        
        if version == current_version:
            # Already at current version
            return data
        
        if version > current_version:
            raise ValueError(f"Schema version {version} is newer than current {current_version}")
        
        # Apply migrations in sequence
        migrated_data = data.copy()
        for migration in self.migrations[schema_type]:
            if version == migration.from_version:
                if migration.validate(migrated_data):
                    migrated_data = migration.migrate(migrated_data)
                    version = migration.to_version
                else:
                    raise ValueError(f"Migration validation failed from {migration.from_version} to {migration.to_version}")
        
        if version != current_version:
            raise ValueError(f"No migration path from {version_str} to {current_version}")
        
        # Update schema version
        migrated_data['schema_version'] = str(current_version)
        
        return migrated_data
    
    def add_version_to_config(self, data: Dict[str, Any], schema_type: SchemaType) -> Dict[str, Any]:
        """Add current schema version to configuration"""
        data['schema_version'] = str(self.CURRENT_VERSIONS[schema_type])
        data['schema_updated'] = datetime.now().isoformat()
        return data
    
    def load_config_with_migration(self, file_path: Path, schema_type: SchemaType) -> Dict[str, Any]:
        """Load configuration file with automatic migration"""
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        # Load file based on extension
        with open(file_path, 'r') as f:
            if file_path.suffix == '.json':
                data = json.load(f)
            else:  # Assume YAML
                data = yaml.safe_load(f)
        
        # Validate and migrate
        migrated_data = self.validate_and_migrate(data, schema_type)
        
        # Save migrated data if changed
        if data != migrated_data:
            self._backup_original(file_path)
            self._save_config(file_path, migrated_data)
            logger.info(f"Migrated {file_path} to schema version {self.CURRENT_VERSIONS[schema_type]}")
        
        return migrated_data
    
    def _backup_original(self, file_path: Path) -> None:
        """Create backup of original file before migration"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = file_path.with_suffix(f'.backup_{timestamp}{file_path.suffix}')
        file_path.rename(backup_path)
        file_path.write_text(backup_path.read_text())
        logger.info(f"Created backup: {backup_path}")
    
    def _save_config(self, file_path: Path, data: Dict[str, Any]) -> None:
        """Save configuration to file"""
        with open(file_path, 'w') as f:
            if file_path.suffix == '.json':
                json.dump(data, f, indent=2)
            else:  # YAML
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)


# Built-in migrations

class AgentSchema_1_0_to_1_1(SchemaMigration):
    """Migration from agent schema 1.0.0 to 1.1.0"""
    
    def __init__(self):
        super().__init__(
            from_version=SchemaVersion(1, 0, 0),
            to_version=SchemaVersion(1, 1, 0)
        )
    
    def migrate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add risk_profile enum support"""
        agents = data.get('agents', {})
        
        for agent_name, agent_data in agents.items():
            # Convert risk_profile string to enum-compatible format
            if 'risk_profile' in agent_data:
                risk_str = agent_data['risk_profile']
                if isinstance(risk_str, str):
                    # Normalize to enum values
                    risk_map = {
                        'conservative': 'conservative',
                        'balanced': 'balanced',
                        'aggressive': 'aggressive',
                        'zero tolerance': 'zero_tolerance',
                        'zero_tolerance': 'zero_tolerance'
                    }
                    agent_data['risk_profile'] = risk_map.get(risk_str.lower(), 'balanced')
            
            # Add new optional fields with defaults
            agent_data.setdefault('version_added', '1.0.0')
            agent_data.setdefault('last_modified', datetime.now().isoformat())
            agent_data.setdefault('tags', [])
            agent_data.setdefault('enabled', True)
        
        return data
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate data structure for migration"""
        return 'agents' in data and isinstance(data['agents'], dict)


class ConfigSchema:
    """Schema definitions for validation"""
    
    AGENT_SCHEMA = {
        "type": "object",
        "required": ["name", "command", "category", "identity", "core_belief"],
        "properties": {
            "name": {"type": "string"},
            "command": {"type": "string", "pattern": "^--[a-z-]+$"},
            "category": {"type": "string", "enum": ["design", "development", "operations", "quality", "architecture"]},
            "identity": {"type": "string"},
            "core_belief": {"type": "string"},
            "primary_question": {"type": "string"},
            "decision_framework": {"type": "string"},
            "risk_profile": {"type": "string", "enum": ["conservative", "balanced", "aggressive", "zero_tolerance"]},
            "success_metrics": {"type": "string"},
            "communication_style": {"type": "string"},
            "problem_solving": {"type": "string"},
            "mcp_preferences": {"type": "array", "items": {"type": "string"}},
            "focus_areas": {"type": "array", "items": {"type": "string"}},
            "values": {"type": "string"},
            "limitations": {"type": "string"},
            "compatible_agents": {"type": "array", "items": {"type": "string"}},
            "handoff_protocols": {"type": "object"},
            "primary_phases": {"type": "array", "items": {"type": "integer", "minimum": 1, "maximum": 10}},
            "support_phases": {"type": "array", "items": {"type": "integer", "minimum": 1, "maximum": 10}},
            "version_added": {"type": "string"},
            "last_modified": {"type": "string"},
            "tags": {"type": "array", "items": {"type": "string"}},
            "enabled": {"type": "boolean"}
        }
    }
    
    PHASE_SCHEMA = {
        "type": "object",
        "required": ["name", "description", "agents", "lead", "outputs"],
        "properties": {
            "name": {"type": "string"},
            "description": {"type": "string"},
            "agents": {"type": "array", "items": {"type": "string"}},
            "lead": {"type": "string"},
            "outputs": {"type": "array", "items": {"type": "string"}},
            "validation": {"type": "array", "items": {"type": "string"}},
            "parallel": {"type": "boolean", "default": False}
        }
    }
    
    @classmethod
    def validate_agent(cls, agent_data: Dict[str, Any]) -> List[str]:
        """Validate agent data against schema, return list of errors"""
        errors = []
        
        # Check required fields
        for field in cls.AGENT_SCHEMA["required"]:
            if field not in agent_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate field types and constraints
        for field, value in agent_data.items():
            if field in cls.AGENT_SCHEMA["properties"]:
                schema = cls.AGENT_SCHEMA["properties"][field]
                
                # Type check
                expected_type = schema.get("type")
                if expected_type == "string" and not isinstance(value, str):
                    errors.append(f"Field {field} must be string, got {type(value).__name__}")
                elif expected_type == "array" and not isinstance(value, list):
                    errors.append(f"Field {field} must be array, got {type(value).__name__}")
                elif expected_type == "object" and not isinstance(value, dict):
                    errors.append(f"Field {field} must be object, got {type(value).__name__}")
                elif expected_type == "boolean" and not isinstance(value, bool):
                    errors.append(f"Field {field} must be boolean, got {type(value).__name__}")
                
                # Enum validation
                if "enum" in schema and value not in schema["enum"]:
                    errors.append(f"Field {field} must be one of {schema['enum']}, got {value}")
                
                # Pattern validation
                if "pattern" in schema and isinstance(value, str):
                    import re
                    if not re.match(schema["pattern"], value):
                        errors.append(f"Field {field} must match pattern {schema['pattern']}, got {value}")
        
        return errors


# Global schema validator instance
_schema_validator = SchemaValidator()


def get_schema_validator() -> SchemaValidator:
    """Get the global schema validator instance"""
    return _schema_validator