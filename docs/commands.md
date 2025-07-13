# Command Reference

Complete reference for all commands in the Unified Agent System.

## CLI Commands

### Basic Commands

```bash
unified-agents [command] [options]
```

| Command | Description | Example |
|---------|-------------|---------|
| `setup` | Initial system setup | `unified-agents setup` |
| `interactive` | Start interactive mode | `unified-agents interactive` |
| `demo` | Run demonstration | `unified-agents demo` |
| `agents` | List all agents | `unified-agents agents` |
| `info` | Get agent information | `unified-agents info backend` |
| `status` | Show system status | `unified-agents status` |
| `version` | Display version | `unified-agents --version` |

### Advanced Commands

| Command | Description | Example |
|---------|-------------|---------|
| `migrate` | Run schema migrations | `unified-agents migrate --apply` |
| `validate` | Validate configurations | `unified-agents validate` |
| `export` | Export configurations | `unified-agents export --format json` |
| `import` | Import configurations | `unified-agents import config.yml` |

## Interactive Mode Commands

Once in interactive mode, all commands start with `/`.

### Agent Commands

#### `/agent` - Manage agents

```bash
# List all agents
/agent --list
/agent -l

# Get agent information
/agent --info <agent_name>
/agent -i backend

# Activate specific agents
/agent --activate "backend,frontend"
/agent -a "qa,security"

# Deactivate agents
/agent --deactivate "mobile"
/agent -d "mobile"

# Show active agents
/agent --active

# Perform agent handoff
/agent --handoff
```

### Execution Commands

#### `/code` - Execute coding tasks

```bash
# Basic usage
/code --backend
/code --frontend
/code --backend --frontend

# With options
/code --backend --file src/api.py
/code --frontend --component Dashboard
/code --mobile --platform ios

# With context
/code --backend --context "implement user authentication"
```

#### `/design` - Execute design tasks

```bash
# UI/UX design
/design --layout_loom
/design --chromatic_architect

# Accessibility review
/design --aura

# Full design team
/design --aura --layout_loom --chromatic_architect

# With specifications
/design --layout_loom --spec "mobile-first dashboard"
```

#### `/test` - Execute testing tasks

```bash
# Quality assurance
/test --qa
/test --security
/test --performance

# Combined testing
/test --qa --security

# With specific targets
/test --qa --file src/components/Login.tsx
/test --security --scan api/
/test --performance --endpoint /api/users
```

#### `/analyze` - Execute analysis tasks

```bash
# Architecture analysis
/analyze --architect
/analyze --api

# With focus area
/analyze --architect --focus scalability
/analyze --api --focus rest-design
```

#### `/deploy` - Execute deployment tasks

```bash
# Standard deployment
/deploy --devops

# Environment-specific
/deploy --devops --env staging
/deploy --devops --env production

# With options
/deploy --devops --rollback
/deploy --devops --dry-run
```

### Workflow Commands

#### `/workflow` - Manage workflows

```bash
# Start workflows
/workflow feature
/workflow bug
/workflow security
/workflow custom

# Workflow management
/workflow --status
/workflow --next
/workflow --previous
/workflow --goto 3
/workflow --abort

# List workflows
/workflow --list
/workflow --info feature
```

### Phase Commands

#### `/phase` - Manage D3P phases

```bash
# Show current phase
/phase --current
/phase -c

# Navigate phases
/phase --next
/phase --previous
/phase --goto 5

# Phase information
/phase --list
/phase --info 3
/phase --requirements  # Show phase requirements
```

### Team Commands

#### `/team` - Manage agent teams

```bash
# Create teams
/team --create "frontend-team" --agents "frontend,aura,chromatic_architect"
/team --create "backend-team" --agents "backend,api,data"

# Activate teams
/team --activate "frontend-team"

# List teams
/team --list
/team --info "frontend-team"

# Remove teams
/team --remove "frontend-team"
```

### Configuration Commands

#### `/config` - Manage configuration

```bash
# Show configuration
/config --show
/config --show agents
/config --show workflows

# Reload configuration
/config --reload

# Edit configuration
/config --edit agents
/config --edit workflows

# Validate configuration
/config --validate
```

### System Commands

#### `/status` - System status

```bash
# Full status
/status

# Specific components
/status --agents
/status --workflows
/status --phase
/status --performance
```

#### `/log` - View logs

```bash
# Recent logs
/log

# Specific count
/log --lines 50

# Filter by level
/log --level ERROR
/log --level DEBUG

# Follow logs
/log --follow
```

#### `/help` - Get help

```bash
# General help
/help

# Command-specific help
/help code
/help workflow
/help agent

# Search help
/help --search "activate"
```

## Command Options

### Global Options

These options work with most commands:

| Option | Short | Description |
|--------|-------|-------------|
| `--verbose` | `-v` | Verbose output |
| `--quiet` | `-q` | Suppress output |
| `--json` | | JSON output format |
| `--no-color` | | Disable colored output |
| `--timeout` | `-t` | Command timeout (seconds) |

### Agent Selection

Multiple ways to specify agents:

```bash
# By name
/code --backend
/code --agent backend

# Multiple agents
/code --agents "backend,frontend"
/code --backend --frontend

# By category
/code --category development
/test --category quality

# By tag
/design --tag accessibility
/code --tag api
```

### Context and Options

Pass additional context to commands:

```bash
# Context string
/code --backend --context "implement OAuth2"

# Options dictionary
/test --qa --options '{"coverage": true, "report": "html"}'

# File targets
/code --backend --file src/auth.py
/test --qa --files "src/,tests/"

# Configuration
/deploy --devops --config deploy.yml
```

## Command Shortcuts

Create aliases for common commands:

```bash
# In interactive mode
/alias cb "/code --backend"
/alias tf "/test --qa --frontend"
/alias dfa "/design --full --all"

# Use aliases
/cb --context "add user endpoints"
/tf --file Login.test.tsx
```

## Batch Commands

Execute multiple commands:

```bash
# Sequential execution
/batch "/analyze --architect; /code --backend; /test --qa"

# Parallel execution
/parallel "/test --qa" "/test --security" "/test --performance"

# From file
/batch --file commands.txt
```

## Command Pipelines

Chain commands together:

```bash
# Pipe output
/analyze --architect | /code --backend

# Conditional execution
/test --qa && /deploy --devops

# Error handling
/code --backend || /log --level ERROR
```

## Advanced Features

### Command History

```bash
# Show history
/history

# Execute from history
/history --exec 5
/!5

# Search history
/history --search "test"
```

### Command Recording

```bash
# Start recording
/record start session1

# Execute commands...

# Stop recording
/record stop

# Replay recording
/record replay session1
```

### Command Templates

```bash
# Save as template
/template save "full-test" "/test --qa --security --performance"

# Use template
/template run "full-test"

# List templates
/template list
```

## Error Handling

### Common Error Codes

| Code | Meaning | Resolution |
|------|---------|------------|
| 1 | Command not found | Check spelling, use `/help` |
| 2 | Invalid arguments | Review command syntax |
| 3 | Agent not available | Check agent name, use `/agent --list` |
| 4 | Workflow error | Check workflow status |
| 5 | Configuration error | Validate configuration |

### Debug Mode

```bash
# Enable debug mode
/debug on

# Run command with debug
/debug /code --backend

# Disable debug mode
/debug off
```

## Best Practices

1. **Use Agent Groups**: Combine related agents for better results
   ```bash
   /code --backend --frontend --api
   ```

2. **Provide Context**: Always include context for better agent responses
   ```bash
   /code --backend --context "implement user authentication with JWT"
   ```

3. **Check Status**: Before major operations
   ```bash
   /status && /deploy --devops --env production
   ```

4. **Use Dry Run**: Test commands safely
   ```bash
   /deploy --devops --dry-run
   ```

5. **Save Templates**: For repeated workflows
   ```bash
   /template save "daily-check" "/test --qa && /status"
   ```

## Quick Reference Card

### Most Used Commands

```bash
# Start working
/agent --activate "backend,frontend"
/phase --current

# Development
/code --backend --frontend
/test --qa

# Review
/analyze --architect
/test --security

# Deploy
/deploy --devops --env staging

# Status check
/status
/workflow --status
```

### Emergency Commands

```bash
# Abort current operation
/abort

# Reset system
/reset --confirm

# Emergency stop
/emergency-stop

# Recovery mode
/recover --from-backup
```