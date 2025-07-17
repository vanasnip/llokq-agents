# MCP Unified Agents Deployment System

A built-in deployment system that enables safe, reliable updates from development to production environments.

## Features

✅ **Version Tracking** - Automatic version management with deployment history  
✅ **Automatic Backups** - Timestamped backups before each deployment  
✅ **Rollback Capability** - Easy rollback to any previous version  
✅ **Deployment Locking** - Prevents concurrent deployments  
✅ **MCP Integration** - Deploy directly from Claude using MCP tools  
✅ **Dry Run Mode** - Preview changes before deploying  
✅ **Smart File Sync** - Only updates changed files  
✅ **Post-Deployment Testing** - Automatic validation after deployment

## Quick Start

### Using MCP Tools (from Claude)

```
# Check deployment status
"Check unified agents deployment status"

# Deploy changes
"Deploy unified agents updates"

# Preview changes without deploying
"Show me what would be deployed (dry run)"

# Rollback to previous version
"Rollback unified agents"
```

### Using Command Line

```bash
# Check status
python deploy.py status

# Deploy changes
python deploy.py deploy

# Preview changes (dry run)
python deploy.py deploy --dry-run

# Rollback to previous version
python deploy.py rollback

# Rollback to specific version
python deploy.py rollback v0.1.0
```

## Configuration

### Environment Variables

```bash
# Development path (defaults to parent of this directory)
export MCP_DEV_PATH=/path/to/dev/mcp-unified-agents

# Production path (defaults to ~/mcp-config/servers/mcp-unified-agents)
export MCP_PROD_PATH=/path/to/prod/mcp-unified-agents

# Backup directory (defaults to ~/.mcp-backups/unified-agents)
export MCP_BACKUP_DIR=/path/to/backups
```

## How It Works

### Deployment Process

1. **Lock Acquisition** - Prevents concurrent deployments
2. **Change Detection** - Compares dev and prod files using SHA256
3. **Backup Creation** - Creates timestamped backup of files to be changed
4. **File Synchronization** - Copies only changed files
5. **Post-Deployment Tests** - Validates Python syntax and JSON files
6. **Version Update** - Records deployment in VERSION file
7. **Lock Release** - Allows future deployments

### Files Synced

The deployment system syncs these file patterns:
- `server.py` - Main MCP server
- `agents.json` - Agent definitions
- `workflow/*.py` - Workflow engine files
- `templates/*.json` - Workflow templates
- `deployment/*.py` - Deployment system itself

### Files Excluded

These files are never deployed:
- `*.pyc`, `__pycache__` - Python cache files
- `.env` - Environment files
- `*.log` - Log files
- `*.tmp` - Temporary files
- `.git` - Git repository
- `VERSION` - Managed separately
- `test_*` - Test files
- `*.bak` - Backup files

## Version Management

Deployments are tracked in a `VERSION` file:

```json
{
  "version": "0.1.2",
  "deployed": "2024-01-20T10:30:00Z",
  "deployed_from": "/Users/ivan/DEV_/agents/mcp-unified-agents",
  "git_commit": "abc123ef",
  "files_updated": ["server.py", "agents.json"],
  "deployed_by": "mcp",
  "history": [...]
}
```

## Backup Strategy

- Backups are created before each deployment
- Stored in `~/.mcp-backups/unified-agents/`
- Named with version and timestamp: `v0.1.0_20240120_103000`
- Only changed files are backed up (incremental)
- Last 10 deployments kept in history

## Error Handling

- **Automatic Rollback** - Failed deployments trigger automatic rollback
- **Lock Cleanup** - Stale locks are automatically cleaned
- **Validation Errors** - Python syntax and JSON validation prevent bad deployments
- **Disk Space** - Pre-flight checks ensure sufficient space

## Testing

Run the test suite:

```bash
python test_deployment.py
```

Tests cover:
- Version management
- Deployment locking
- File synchronization
- Rollback functionality
- Error scenarios

## Troubleshooting

### Deployment Locked

If deployment is locked:
```bash
python deploy.py status  # Check who has the lock
```

Locks auto-expire after 30 minutes or if the process dies.

### Failed Deployment

Failed deployments automatically rollback. Check logs:
```bash
tail -f ~/.mcp-deployment/deployments.log
```

### Manual Rollback

List available backups:
```bash
ls -la ~/.mcp-backups/unified-agents/
```

Rollback to specific backup:
```bash
python deploy.py rollback v0.1.0
```

## Architecture

```
deployment/
├── __init__.py              # Package initialization
├── version_manager.py       # Version tracking and history
├── deployment_lock.py       # Concurrent deployment prevention
├── deployment_manager.py    # Main deployment logic
└── README.md               # This file
```

## Future Enhancements

Phase 2 additions will include:
- Health check integration
- Deployment profiles (dev/staging/prod)
- Metrics and monitoring
- Webhook notifications
- CI/CD integration

## Contributing

When modifying the deployment system:
1. Update tests in `test_deployment.py`
2. Test both MCP tools and CLI usage
3. Update this README if needed
4. Ensure backward compatibility