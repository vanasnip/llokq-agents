# Schema Migration CLI Command

This guide explains how to use the schema migration CLI command to manage configuration schema versions and migrations in the Unified Agent System.

## Overview

The schema migration system ensures smooth upgrades when configuration formats change. It automatically detects version mismatches and applies necessary transformations to update configurations to the latest schema version.

## Installation

The migration command is available through the unified CLI:

```bash
# Run from project root
python -m unified.cli migrate [options]
```

Or create an alias:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias unified-migrate="python -m unified.cli migrate"
```

## Basic Usage

### Check Current Schema Versions

```bash
# Show current schema versions
python -m unified.cli migrate --status

# Output:
Schema Status:
  Agent Schema: v1.1.0 (latest)
  Phase Schema: v1.0.0 (latest)
  Workflow Schema: v1.0.0 (latest)
```

### Validate Configurations

```bash
# Validate all configurations
python -m unified.cli migrate --validate

# Validate specific type
python -m unified.cli migrate --validate --type agent

# Validate specific file
python -m unified.cli migrate --validate --file agents/code_executor.yaml
```

### Apply Migrations

```bash
# Dry run - show what would change
python -m unified.cli migrate --dry-run

# Apply all pending migrations
python -m unified.cli migrate --apply

# Apply migrations for specific type
python -m unified.cli migrate --apply --type agent

# Force migration even if up-to-date
python -m unified.cli migrate --apply --force
```

## Command Options

| Option | Description |
|--------|-------------|
| `--status` | Show current schema versions |
| `--validate` | Validate configurations without migrating |
| `--apply` | Apply pending migrations |
| `--dry-run` | Preview changes without applying |
| `--type TYPE` | Target specific schema type (agent, phase, workflow) |
| `--file FILE` | Target specific configuration file |
| `--backup` | Create backups before migration (default: true) |
| `--no-backup` | Skip backup creation |
| `--force` | Force migration even if already current |
| `--quiet` | Suppress non-error output |
| `--verbose` | Show detailed migration steps |

## Migration Process

### 1. Detection Phase

The migrator scans for configuration files:

```bash
python -m unified.cli migrate --validate

Scanning for configurations...
Found 15 agent configurations
Found 5 phase configurations
Found 3 workflow configurations

Validation Results:
  ✓ 15/15 agents valid (v1.0.0)
  ⚠ 3/5 phases need migration (v0.9.0 → v1.0.0)
  ✓ 3/3 workflows valid (v1.0.0)
```

### 2. Backup Phase

Before applying migrations, backups are created:

```bash
python -m unified.cli migrate --apply

Creating backups...
  ✓ Backed up code_executor.yaml → code_executor.yaml.backup
  ✓ Backed up phases/design.yaml → phases/design.yaml.backup
```

### 3. Migration Phase

Migrations are applied with detailed logging:

```bash
Applying migrations...

Migrating phases/design.yaml (v0.9.0 → v1.0.0):
  ↻ Converting 'tools' array to 'tool_preferences' object
  ↻ Adding 'validation_rules' with defaults
  ✓ Migration complete

Summary:
  ✓ 3 files migrated successfully
  ✓ 0 errors
  ✓ All configurations now at latest version
```

## Writing Custom Migrations

### Migration Structure

Create migrations in `unified/migrations/`:

```python
# unified/migrations/agent_v1_0_to_v1_1.py
from unified.core.schema_version import Migration, SchemaType, SchemaVersion

class AgentV10ToV11(Migration):
    """Migrate agent schema from v1.0.0 to v1.1.0"""
    
    @property
    def from_version(self) -> SchemaVersion:
        return SchemaVersion(1, 0, 0)
    
    @property
    def to_version(self) -> SchemaVersion:
        return SchemaVersion(1, 1, 0)
    
    @property
    def schema_type(self) -> SchemaType:
        return SchemaType.AGENT
    
    def migrate(self, data: dict) -> dict:
        """Apply migration transformations"""
        # Add new required field with default
        if 'mcp_preferences' not in data:
            data['mcp_preferences'] = ['filesystem']
        
        # Convert old format to new
        if 'tools' in data:
            data['tool_preferences'] = {
                tool: 'preferred' for tool in data.pop('tools')
            }
        
        # Update version
        data['schema_version'] = str(self.to_version)
        
        return data
    
    def validate(self, data: dict) -> List[str]:
        """Validate migrated data"""
        errors = []
        
        if 'mcp_preferences' not in data:
            errors.append("Missing required field: mcp_preferences")
        
        if not isinstance(data.get('tool_preferences'), dict):
            errors.append("tool_preferences must be a dictionary")
        
        return errors
```

### Registering Migrations

Add to `unified/migrations/__init__.py`:

```python
from .agent_v1_0_to_v1_1 import AgentV10ToV11

MIGRATIONS = [
    AgentV10ToV11(),
    # Add new migrations here
]
```

## Advanced Usage

### Batch Operations

```bash
# Migrate all YAML files in a directory
find agents/ -name "*.yaml" -exec python -m unified.cli migrate --apply --file {} \;

# Validate all configurations in CI
python -m unified.cli migrate --validate --quiet || exit 1
```

### Integration with CI/CD

```yaml
# .github/workflows/validate.yml
- name: Validate Schemas
  run: |
    python -m unified.cli migrate --validate
    if [ $? -ne 0 ]; then
      echo "Schema validation failed"
      exit 1
    fi
```

### Programmatic Usage

```python
from unified.cli.commands.migrate import MigrationCommand
from pathlib import Path

# Create command instance
cmd = MigrationCommand()

# Validate specific file
result = cmd.validate_file(Path("agents/code_executor.yaml"))
if not result.is_valid:
    print(f"Validation errors: {result.errors}")

# Apply migrations programmatically
results = cmd.apply_migrations(
    schema_type="agent",
    dry_run=False,
    backup=True
)

for result in results:
    print(f"{result.file}: {result.status}")
```

## Troubleshooting

### Common Issues

#### 1. Migration Fails

```bash
Error: Migration failed for agents/test.yaml
Reason: Invalid YAML syntax at line 15

Solution:
1. Fix YAML syntax errors first
2. Run validation: python -m unified.cli migrate --validate --file agents/test.yaml
3. Retry migration
```

#### 2. Backup Conflicts

```bash
Error: Backup file already exists: code_executor.yaml.backup

Solution:
1. Remove or rename existing backup
2. Use --no-backup to skip backups
3. Use --force to overwrite
```

#### 3. Version Conflicts

```bash
Error: Cannot migrate from v0.8.0 to v1.1.0 directly

Solution:
1. Check available migration path
2. May need intermediate migrations
3. Contact support if migration path missing
```

### Recovery

If migration fails:

```bash
# Restore from backup
mv agents/code_executor.yaml.backup agents/code_executor.yaml

# Or restore all backups
for f in $(find . -name "*.backup"); do
  mv "$f" "${f%.backup}"
done
```

## Best Practices

1. **Always Test First**: Run with `--dry-run` before applying
2. **Keep Backups**: Don't use `--no-backup` in production
3. **Validate in CI**: Add schema validation to your CI pipeline
4. **Document Changes**: Update migration guide when adding new migrations
5. **Version Control**: Commit after successful migrations

## Schema Version History

### Agent Schema

- **v1.1.0** (Current)
  - Added `mcp_preferences` field
  - Converted `tools` to `tool_preferences`
  - Added `validation_rules`

- **v1.0.0**
  - Initial stable release
  - Basic agent configuration

### Phase Schema

- **v1.0.0** (Current)
  - Initial stable release
  - Phase workflow configuration

### Workflow Schema

- **v1.0.0** (Current)
  - Initial stable release
  - Workflow orchestration configuration

## Future Enhancements

Planned features for the migration CLI:

1. **Rollback Support**: Undo migrations to previous versions
2. **Migration History**: Track applied migrations
3. **Custom Migration Hooks**: Pre/post migration scripts
4. **Batch Migration UI**: Interactive migration wizard
5. **Schema Registry**: Central schema version registry

## Examples

### Example 1: Full Migration Workflow

```bash
# 1. Check status
$ python -m unified.cli migrate --status
Schema Status:
  Agent Schema: v1.0.0 (update available: v1.1.0)

# 2. Preview changes
$ python -m unified.cli migrate --dry-run
Would migrate 15 agent configurations:
  - Add mcp_preferences field
  - Convert tools to tool_preferences

# 3. Apply migrations
$ python -m unified.cli migrate --apply --verbose
Creating backups...
Migrating agents/code_executor.yaml...
  + Added mcp_preferences: ['filesystem', 'git']
  ↻ Converted tools → tool_preferences
  ✓ Success

# 4. Verify
$ python -m unified.cli migrate --status
Schema Status:
  Agent Schema: v1.1.0 (latest)
```

### Example 2: Selective Migration

```bash
# Migrate only specific agents
$ python -m unified.cli migrate --apply --file agents/qa_specialist.yaml

# Migrate only phase configurations
$ python -m unified.cli migrate --apply --type phase
```

### Example 3: CI Integration

```bash
#!/bin/bash
# ci-validate.sh

echo "Validating schema versions..."
python -m unified.cli migrate --validate --quiet

if [ $? -eq 0 ]; then
    echo "✓ All schemas valid"
else
    echo "✗ Schema validation failed"
    python -m unified.cli migrate --validate  # Show details
    exit 1
fi
```