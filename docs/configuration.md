# Configuration Guide

Comprehensive guide to configuring the Unified Agent System.

## Configuration Overview

The system uses YAML configuration files stored in `~/.claude/`:

```
~/.claude/
├── agents.yml         # Agent definitions and preferences
├── workflows.yml      # Workflow configurations
├── settings.yml       # System-wide settings
├── templates/         # Command and workflow templates
└── logs/             # Application logs
```

## Agent Configuration

### Basic Agent Structure

In `~/.claude/agents.yml`:

```yaml
agent_name:
  # Identity
  identity: "Backend Development Specialist"
  category: "development"
  
  # Core attributes
  core_belief: "Data integrity is paramount"
  primary_question: "How can we ensure data consistency?"
  decision_framework: "reliability_first"
  problem_solving: "systematic_debugging"
  
  # Behavioral traits
  communication_style: "precise"
  collaboration_approach: "detail_oriented"
  
  # Tool preferences
  mcp_preferences:
    - filesystem
    - git
    - shell
    - database
  
  # Operational settings
  focus_areas:
    - "API development"
    - "Database optimization"
    - "Authentication"
  
  success_metrics:
    - "Code coverage > 90%"
    - "API response time < 200ms"
    - "Zero security vulnerabilities"
  
  # Compatibility
  compatible_agents:
    - frontend
    - api
    - qa
```

### Advanced Agent Features

#### Custom Context

Add agent-specific context:

```yaml
backend:
  custom_context: |
    Always follow SOLID principles.
    Prefer composition over inheritance.
    Use dependency injection for testability.
    Document all public APIs.
```

#### Conditional Behavior

Configure behavior based on conditions:

```yaml
security:
  behavior_rules:
    - condition: "environment == 'production'"
      action: "enforce_strict_validation"
    - condition: "sensitive_data == true"
      action: "enable_encryption"
```

#### Tool Configuration

Specify tool-specific settings:

```yaml
devops:
  tool_configs:
    kubernetes:
      namespace: "default"
      context: "production"
    terraform:
      backend: "s3"
      workspace: "prod"
```

## Workflow Configuration

### Basic Workflow

In `~/.claude/workflows.yml`:

```yaml
workflows:
  feature_development:
    name: "Feature Development"
    description: "End-to-end feature development"
    
    phases:
      - name: "Requirements"
        agents: ["riley", "architect"]
        duration: "2 days"
        outputs:
          - requirements.md
          - technical-spec.md
      
      - name: "Implementation"
        agents: ["backend", "frontend"]
        parallel: true
        duration: "5 days"
        outputs:
          - src/
          - tests/
```

### Advanced Workflow Features

#### Dynamic Workflows

```yaml
adaptive_workflow:
  name: "Adaptive Development"
  
  initial_assessment:
    agent: "architect"
    determines: "workflow_path"
  
  paths:
    simple:
      phases: ["quick_design", "rapid_development", "basic_test"]
    
    complex:
      phases: ["detailed_design", "phased_development", "comprehensive_test"]
    
    critical:
      phases: ["security_review", "formal_design", "secure_development", "penetration_test"]
```

#### Workflow Variables

```yaml
parameterized_workflow:
  name: "Configurable Deploy"
  
  variables:
    - name: "environment"
      type: "string"
      required: true
      values: ["dev", "staging", "prod"]
    
    - name: "rollback_enabled"
      type: "boolean"
      default: true
    
    - name: "notification_channels"
      type: "array"
      default: ["slack", "email"]
  
  phases:
    - name: "Deploy"
      condition: "environment != 'prod' || approval == true"
      agents: ["devops"]
      config:
        environment: "${environment}"
        rollback: "${rollback_enabled}"
```

## System Settings

### General Settings

In `~/.claude/settings.yml`:

```yaml
system:
  # Logging
  log_level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  log_format: "json"  # json, text
  log_file: "~/.claude/logs/unified.log"
  log_rotation: "daily"
  log_retention_days: 30
  
  # Performance
  max_parallel_agents: 4
  agent_timeout_seconds: 300
  workflow_checkpoint_interval: 60
  
  # Security
  enable_sandboxing: true
  sandbox_memory_limit_mb: 512
  command_whitelist_enabled: true
  
  # UI/UX
  color_output: true
  progress_indicators: true
  interactive_mode_default: true
  auto_complete: true
```

### Integration Settings

```yaml
integrations:
  github:
    enabled: true
    token_env: "GITHUB_TOKEN"
    default_org: "your-org"
    
  openai:
    enabled: true
    api_key_env: "OPENAI_API_KEY"
    model: "gpt-4"
    max_tokens: 4000
    
  slack:
    enabled: false
    webhook_env: "SLACK_WEBHOOK"
    default_channel: "#dev-updates"
```

### Feature Flags

```yaml
features:
  # Experimental features
  async_workflows: true
  distributed_agents: false
  web_ui: false
  
  # Beta features
  auto_documentation: true
  smart_suggestions: true
  workflow_recording: true
  
  # Security features
  input_validation: true
  command_sandboxing: true
  audit_logging: true
```

## Environment Variables

Override configuration with environment variables:

```bash
# System settings
export UNIFIED_LOG_LEVEL=DEBUG
export UNIFIED_CONFIG_DIR=~/.my-claude
export UNIFIED_CACHE_DIR=/tmp/unified-cache

# Integration tokens
export GITHUB_TOKEN=ghp_xxxxx
export OPENAI_API_KEY=sk-xxxxx
export ANTHROPIC_API_KEY=ak-xxxxx

# Feature flags
export UNIFIED_FEATURE_ASYNC=true
export UNIFIED_FEATURE_SANDBOX=false

# Performance tuning
export UNIFIED_MAX_WORKERS=8
export UNIFIED_TIMEOUT=600
```

## Template Configuration

### Command Templates

In `~/.claude/templates/commands.yml`:

```yaml
command_templates:
  full_stack:
    description: "Full stack development"
    command: "/code --backend --frontend --api"
    
  security_audit:
    description: "Complete security audit"
    command: "/analyze --security && /test --security && /workflow security"
    
  quick_fix:
    description: "Quick bug fix workflow"
    command: "/workflow bug --quick --skip-phases 1,2"
```

### Workflow Templates

```yaml
workflow_templates:
  microservice:
    base_workflow: "feature_development"
    customizations:
      phases:
        - insert_after: "architecture"
          phase:
            name: "Service Design"
            agents: ["architect", "api"]
            outputs: ["service-spec.yml"]
```

## Configuration Profiles

### Multiple Profiles

Create different profiles for different contexts:

```yaml
# ~/.claude/profiles/startup.yml
profiles:
  startup:
    settings:
      max_parallel_agents: 2
      agent_timeout_seconds: 120
    
    workflows:
      default: "rapid_development"
    
    agents:
      priorities: ["backend", "frontend", "qa"]

# ~/.claude/profiles/enterprise.yml
profiles:
  enterprise:
    settings:
      enable_audit_logging: true
      require_approval: true
    
    workflows:
      default: "enterprise_sdlc"
    
    agents:
      priorities: ["security", "compliance", "architect"]
```

### Profile Activation

```bash
# Activate profile
unified-agents --profile startup

# Or via environment
export UNIFIED_PROFILE=enterprise
```

## Security Configuration

### Access Control

```yaml
security:
  access_control:
    enabled: true
    
    roles:
      developer:
        allowed_commands: ["code", "test", "analyze"]
        forbidden_agents: ["devops"]
        
      lead:
        allowed_commands: ["*"]
        approval_required: ["deploy"]
        
      admin:
        allowed_commands: ["*"]
        sudo_mode: true
```

### Audit Configuration

```yaml
audit:
  enabled: true
  
  log_events:
    - "command_execution"
    - "workflow_start"
    - "agent_activation"
    - "configuration_change"
  
  retention_days: 90
  
  destinations:
    - type: "file"
      path: "~/.claude/audit/audit.log"
    
    - type: "syslog"
      host: "syslog.company.com"
      port: 514
```

## Performance Tuning

### Agent Performance

```yaml
performance:
  agents:
    # Cache settings
    cache_enabled: true
    cache_ttl_seconds: 3600
    cache_size_mb: 100
    
    # Execution settings
    parallel_execution: true
    batch_size: 10
    queue_size: 100
    
    # Resource limits
    cpu_limit: "2.0"
    memory_limit_mb: 1024
    disk_io_limit_mbps: 100
```

### Workflow Optimization

```yaml
workflow_optimization:
  # Checkpointing
  checkpoint_enabled: true
  checkpoint_interval_seconds: 300
  checkpoint_retention: 5
  
  # Parallelization
  auto_parallelize: true
  max_parallel_phases: 3
  
  # Caching
  cache_phase_outputs: true
  reuse_unchanged_outputs: true
```

## Migration Configuration

### Schema Versions

```yaml
schema_versions:
  current:
    agents: "1.1.0"
    workflows: "1.0.0"
    settings: "1.0.0"
  
  migration_policy: "auto"  # auto, manual, notify
  backup_before_migration: true
  migration_log: "~/.claude/migrations/history.log"
```

## Validation Rules

### Configuration Validation

```yaml
validation:
  strict_mode: true
  
  rules:
    agents:
      required_fields: ["identity", "category", "mcp_preferences"]
      name_pattern: "^[a-z_]+$"
      max_name_length: 30
    
    workflows:
      required_fields: ["name", "phases"]
      max_phases: 20
      output_path_pattern: "^[a-zA-Z0-9/_.-]+$"
```

## Troubleshooting Configuration

### Debug Settings

```yaml
debug:
  # Verbose output
  verbose_commands: ["workflow", "agent"]
  trace_agents: ["backend", "security"]
  
  # Debug files
  dump_context: true
  context_dir: "~/.claude/debug/context/"
  
  # Performance profiling
  profile_enabled: false
  profile_output: "~/.claude/debug/profile/"
```

### Common Issues

1. **Configuration Not Loading**
   ```bash
   # Check configuration path
   unified-agents config --check
   
   # Validate configuration
   unified-agents config --validate
   
   # Show effective configuration
   unified-agents config --show-effective
   ```

2. **Agent Not Found**
   ```bash
   # Regenerate agent configuration
   unified-agents setup --regenerate-agents
   
   # Check agent status
   unified-agents agent --status backend
   ```

3. **Workflow Errors**
   ```bash
   # Validate workflow
   unified-agents workflow --validate feature
   
   # Test workflow
   unified-agents workflow --dry-run feature
   ```

## Best Practices

1. **Version Control**: Keep configurations in git
   ```bash
   cd ~/.claude
   git init
   git add -A
   git commit -m "Initial configuration"
   ```

2. **Environment Separation**: Use profiles for different environments
   ```bash
   # Development
   unified-agents --profile dev
   
   # Production
   unified-agents --profile prod
   ```

3. **Regular Validation**: Add to CI/CD
   ```bash
   unified-agents config --validate || exit 1
   ```

4. **Incremental Changes**: Test configuration changes
   ```bash
   # Test with dry-run
   unified-agents --config-file test.yml --dry-run
   ```

5. **Documentation**: Document custom configurations
   ```yaml
   # Document why this setting exists
   custom_setting: true  # Required for ACME Corp integration
   ```