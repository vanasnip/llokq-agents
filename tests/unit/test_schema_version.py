"""
Unit tests for Schema Versioning
"""
import pytest
from datetime import datetime
from pathlib import Path
import tempfile
import yaml
import json
from unified.core.schema_version import (
    SchemaVersion, SchemaType, SchemaMigration, SchemaValidator,
    AgentSchema_1_0_to_1_1, ConfigSchema, get_schema_validator
)


class TestSchemaVersion:
    """Test SchemaVersion functionality"""
    
    def test_schema_version_creation(self):
        """Test creating schema version"""
        version = SchemaVersion(1, 2, 3)
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3
        assert str(version) == "1.2.3"
    
    def test_schema_version_from_string(self):
        """Test parsing version from string"""
        version = SchemaVersion.from_string("2.1.0")
        assert version.major == 2
        assert version.minor == 1
        assert version.patch == 0
    
    def test_schema_version_invalid_format(self):
        """Test invalid version string format"""
        with pytest.raises(ValueError, match="Invalid version format"):
            SchemaVersion.from_string("1.2")
        
        with pytest.raises(ValueError):
            SchemaVersion.from_string("invalid")
    
    def test_schema_version_comparison(self):
        """Test version comparison"""
        v1 = SchemaVersion(1, 0, 0)
        v2 = SchemaVersion(1, 1, 0)
        v3 = SchemaVersion(2, 0, 0)
        v4 = SchemaVersion(1, 1, 0)
        
        assert v1 < v2
        assert v2 < v3
        assert v2 == v4
        assert not v3 < v2


class TestSchemaMigration:
    """Test schema migration functionality"""
    
    def test_agent_migration_1_0_to_1_1(self):
        """Test agent schema migration from 1.0.0 to 1.1.0"""
        migration = AgentSchema_1_0_to_1_1()
        
        # Test data
        old_data = {
            'agents': {
                'backend': {
                    'name': 'backend',
                    'risk_profile': 'conservative'
                },
                'security': {
                    'name': 'security',
                    'risk_profile': 'zero tolerance'
                }
            }
        }
        
        # Apply migration
        new_data = migration.migrate(old_data)
        
        # Verify risk_profile conversion
        assert new_data['agents']['backend']['risk_profile'] == 'conservative'
        assert new_data['agents']['security']['risk_profile'] == 'zero_tolerance'
        
        # Verify new fields added
        assert 'version_added' in new_data['agents']['backend']
        assert 'last_modified' in new_data['agents']['backend']
        assert 'tags' in new_data['agents']['backend']
        assert new_data['agents']['backend']['enabled'] is True
    
    def test_migration_validation(self):
        """Test migration validation"""
        migration = AgentSchema_1_0_to_1_1()
        
        # Valid data
        assert migration.validate({'agents': {}}) is True
        
        # Invalid data
        assert migration.validate({}) is False
        assert migration.validate({'agents': 'not_dict'}) is False


class TestSchemaValidator:
    """Test SchemaValidator functionality"""
    
    @pytest.fixture
    def validator(self):
        """Create SchemaValidator instance"""
        return SchemaValidator()
    
    def test_current_versions(self, validator):
        """Test current schema versions"""
        assert validator.CURRENT_VERSIONS[SchemaType.AGENT] == SchemaVersion(1, 1, 0)
        assert validator.CURRENT_VERSIONS[SchemaType.PHASE] == SchemaVersion(1, 0, 0)
    
    def test_validate_and_migrate_current_version(self, validator):
        """Test validation when already at current version"""
        data = {
            'schema_version': '1.1.0',
            'agents': {}
        }
        
        result = validator.validate_and_migrate(data, SchemaType.AGENT)
        assert result == data  # No changes
    
    def test_validate_and_migrate_old_version(self, validator):
        """Test migration from old version"""
        data = {
            'schema_version': '1.0.0',
            'agents': {
                'test': {
                    'risk_profile': 'zero tolerance'
                }
            }
        }
        
        result = validator.validate_and_migrate(data, SchemaType.AGENT)
        
        assert result['schema_version'] == '1.1.0'
        assert result['agents']['test']['risk_profile'] == 'zero_tolerance'
        assert 'tags' in result['agents']['test']
    
    def test_validate_newer_version_error(self, validator):
        """Test error when schema version is newer than current"""
        data = {
            'schema_version': '2.0.0',
            'agents': {}
        }
        
        with pytest.raises(ValueError, match="newer than current"):
            validator.validate_and_migrate(data, SchemaType.AGENT)
    
    def test_add_version_to_config(self, validator):
        """Test adding version to configuration"""
        data = {'agents': {}}
        
        result = validator.add_version_to_config(data, SchemaType.AGENT)
        
        assert result['schema_version'] == '1.1.0'
        assert 'schema_updated' in result
        
        # Verify timestamp format
        datetime.fromisoformat(result['schema_updated'])
    
    def test_load_config_with_migration_yaml(self, validator):
        """Test loading YAML config with migration"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump({
                'schema_version': '1.0.0',
                'agents': {
                    'test': {'risk_profile': 'conservative'}
                }
            }, f)
            temp_path = Path(f.name)
        
        try:
            result = validator.load_config_with_migration(temp_path, SchemaType.AGENT)
            
            assert result['schema_version'] == '1.1.0'
            assert result['agents']['test']['risk_profile'] == 'conservative'
            assert 'enabled' in result['agents']['test']
            
            # Verify backup was created
            backups = list(temp_path.parent.glob(f"{temp_path.stem}.backup_*"))
            assert len(backups) == 1
            
        finally:
            temp_path.unlink()
            for backup in temp_path.parent.glob(f"{temp_path.stem}.backup_*"):
                backup.unlink()
    
    def test_load_config_with_migration_json(self, validator):
        """Test loading JSON config with migration"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                'schema_version': '1.0.0',
                'agents': {}
            }, f)
            temp_path = Path(f.name)
        
        try:
            result = validator.load_config_with_migration(temp_path, SchemaType.AGENT)
            assert result['schema_version'] == '1.1.0'
        finally:
            temp_path.unlink()
            for backup in temp_path.parent.glob(f"{temp_path.stem}.backup_*"):
                backup.unlink()
    
    def test_load_nonexistent_config(self, validator):
        """Test loading nonexistent config file"""
        with pytest.raises(FileNotFoundError):
            validator.load_config_with_migration(Path("/nonexistent.yml"), SchemaType.AGENT)


class TestConfigSchema:
    """Test schema validation definitions"""
    
    def test_validate_agent_valid(self):
        """Test validating valid agent data"""
        agent_data = {
            'name': 'test',
            'command': '--test',
            'category': 'development',
            'identity': 'Test agent',
            'core_belief': 'Testing is important',
            'risk_profile': 'balanced',
            'mcp_preferences': ['filesystem'],
            'enabled': True
        }
        
        errors = ConfigSchema.validate_agent(agent_data)
        assert len(errors) == 0
    
    def test_validate_agent_missing_required(self):
        """Test validating agent with missing required fields"""
        agent_data = {
            'name': 'test',
            'category': 'development'
        }
        
        errors = ConfigSchema.validate_agent(agent_data)
        assert len(errors) > 0
        assert any('command' in e for e in errors)
        assert any('identity' in e for e in errors)
        assert any('core_belief' in e for e in errors)
    
    def test_validate_agent_invalid_types(self):
        """Test validating agent with invalid field types"""
        agent_data = {
            'name': 'test',
            'command': '--test',
            'category': 'development',
            'identity': 'Test',
            'core_belief': 'Test',
            'mcp_preferences': 'not_a_list',  # Should be array
            'enabled': 'yes'  # Should be boolean
        }
        
        errors = ConfigSchema.validate_agent(agent_data)
        assert any('mcp_preferences' in e and 'array' in e for e in errors)
        assert any('enabled' in e and 'boolean' in e for e in errors)
    
    def test_validate_agent_invalid_enum(self):
        """Test validating agent with invalid enum values"""
        agent_data = {
            'name': 'test',
            'command': '--test',
            'category': 'invalid_category',
            'identity': 'Test',
            'core_belief': 'Test',
            'risk_profile': 'invalid_risk'
        }
        
        errors = ConfigSchema.validate_agent(agent_data)
        assert any('category' in e and 'must be one of' in e for e in errors)
        assert any('risk_profile' in e and 'must be one of' in e for e in errors)
    
    def test_validate_agent_invalid_pattern(self):
        """Test validating agent with invalid pattern"""
        agent_data = {
            'name': 'test',
            'command': 'test',  # Should start with --
            'category': 'development',
            'identity': 'Test',
            'core_belief': 'Test'
        }
        
        errors = ConfigSchema.validate_agent(agent_data)
        assert any('command' in e and 'pattern' in e for e in errors)


def test_global_schema_validator():
    """Test global schema validator instance"""
    validator = get_schema_validator()
    assert isinstance(validator, SchemaValidator)
    assert len(validator.migrations[SchemaType.AGENT]) > 0