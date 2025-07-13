# Unified Agent System Architecture

## Overview

The Unified Agent System combines the rich agent definitions from D3P (Dialogue-Driven Development Protocol) with the elegant command structure of SuperClaude. This architecture document outlines the key design decisions, patterns, and components that make up the system.

## Architecture Principles

### 1. **Single Source of Truth**
- Agent state is managed centrally by `AgentManager`
- All components communicate through the Event Bus
- Configuration files use versioned schemas

### 2. **Loose Coupling**
- Components communicate via events, not direct calls
- Plugins can extend functionality without modifying core
- Async operations are isolated from sync code

### 3. **Progressive Enhancement**
- System works with basic sync operations
- Async capabilities enhance but don't replace sync
- Features can be disabled without breaking core functionality

### 4. **Schema Evolution**
- All configurations are versioned
- Automatic migration preserves compatibility
- Backward compatibility for at least 2 major versions

## Core Components

### Agent System (`unified.agents`)

```
┌─────────────────┐     ┌──────────────┐
│  AgentManager   │────▶│    Agent     │
│                 │     │  (dataclass) │
│  - agents: Dict │     └──────────────┘
│  - active: Set  │            │
└────────┬────────┘            │
         │                     ▼
         │              ┌──────────────┐
         └─────────────▶│ AgentCategory│
                        │    (enum)    │
                        └──────────────┘
```

**Key Decisions:**
- Agents are immutable dataclasses for thread safety
- Manager maintains activation state separately from agent definitions
- Event bus integration for state change notifications

### Event Bus (`unified.core.event_bus`)

```
┌─────────────────┐
│    EventBus     │
│                 │     ┌──────────────┐
│  - handlers     │────▶│    Event     │
│  - async_handlers│    │              │
│  - middleware   │     │ - type       │
└────────┬────────┘     │ - data       │
         │              │ - source     │
         │              │ - timestamp  │
         ▼              └──────────────┘
   ┌─────────────┐
   │  EventType  │
   │   (enum)    │
   └─────────────┘
```

**Key Decisions:**
- Supports both sync and async handlers
- Middleware for cross-cutting concerns
- Event history for debugging and replay
- Correlation IDs for tracing related events

### Workflow Engine (`unified.workflows`)

#### Synchronous Engine
```
┌─────────────────┐     ┌──────────────┐
│ WorkflowEngine  │────▶│   Workflow   │
│                 │     │              │
│ - sequential    │     │ - steps[]    │
│ - state tracking│     │ - agents[]   │
└─────────────────┘     └──────────────┘
```

#### Asynchronous Engine
```
┌─────────────────┐     ┌──────────────┐
│AsyncWorkflowEngine│───▶│WorkflowStep  │
│                 │     │              │
│ - parallel exec │     │ - depends_on │
│ - retry logic   │     │ - timeout    │
│ - cancellation  │     │ - parallel   │
└─────────────────┘     └──────────────┘
```

**Key Decisions:**
- Separate sync and async engines for clarity
- Dependency graph for parallel execution
- Step-level retry and timeout configuration
- Background task management

### Command System (`unified.core`)

```
┌─────────────────┐     ┌──────────────┐     ┌──────────────┐
│ CommandParser   │────▶│ParsedCommand │────▶│CommandExecutor│
│                 │     │              │     │              │
│ - parse()       │     │ - base_cmd   │     │ - execute()  │
│ - validate()    │     │ - agents[]   │     │ - context    │
└─────────────────┘     │ - options    │     └──────────────┘
                        └──────────────┘              │
                                                      ▼
                                              ┌──────────────┐
                                              │AsyncExecutor │
                                              │              │
                                              │ - parallel   │
                                              │ - timeout    │
                                              └──────────────┘
```

**Key Decisions:**
- Command parsing separate from execution
- Agent context applied at execution time
- Async wrapper for non-blocking operations
- MCP preferences aggregated from active agents

### Phase Management (`unified.core.phase_manager`)

```
┌─────────────────┐     ┌──────────────┐
│  PhaseManager   │────▶│    Phase     │
│                 │     │              │
│ - current_phase │     │ - agents[]   │
│ - artifacts     │     │ - outputs[]  │
│ - transitions   │     │ - parallel   │
└─────────────────┘     └──────────────┘
```

**Key Decisions:**
- Phases track required outputs for completion
- Automatic agent activation on phase change
- Event notifications for phase transitions
- Support for parallel agent execution within phases

### Schema Versioning (`unified.core.schema_version`)

```
┌─────────────────┐     ┌──────────────┐
│SchemaValidator  │────▶│SchemaVersion │
│                 │     │              │
│ - migrations[]  │     │ - major      │
│ - validate()    │     │ - minor      │
│ - migrate()     │     │ - patch      │
└─────────────────┘     └──────────────┘
         │
         ▼
┌─────────────────┐
│SchemaMigration  │
│                 │
│ - from_version  │
│ - to_version    │
│ - migrate()     │
└─────────────────┘
```

**Key Decisions:**
- Semantic versioning for all schemas
- Automatic backup before migration
- Migration path validation
- Schema validation using JSON Schema patterns

## Event Flow

### Agent Activation Flow
```
User Command → CommandParser → AgentManager.activate_agent()
                                      │
                                      ▼
                              Event: AGENT_ACTIVATED
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
            PhaseManager      WorkflowEngine    CommandExecutor
            (update phase)    (update state)    (apply context)
```

### Workflow Execution Flow
```
Start Workflow → AsyncWorkflowEngine → Analyze Dependencies
                                             │
                                             ▼
                                    Execute Parallel Steps
                                             │
                         ┌───────────────────┼───────────────────┐
                         ▼                   ▼                   ▼
                    Step A              Step B              Step C
                    (agents)            (agents)            (agents)
                         │                   │                   │
                         └───────────────────┴───────────────────┘
                                             │
                                             ▼
                                    Event: WORKFLOW_COMPLETED
```

## Extension Points

### 1. **Custom Agents**
- Add new agent definitions to configuration
- Implement agent-specific executors
- Register custom MCP preferences

### 2. **Workflow Steps**
- Register custom step executors
- Define new workflow templates
- Implement domain-specific retry logic

### 3. **Event Handlers**
- Subscribe to system events
- Add middleware for logging/metrics
- Implement custom event types

### 4. **Schema Migrations**
- Define migration classes for schema updates
- Implement custom validation rules
- Add new schema types

## Security Considerations

### Input Validation
- All user commands are parsed and validated
- Agent names are checked against whitelist
- Command options are sanitized

### Execution Isolation
- Commands execute in controlled context
- File system access limited by working directory
- Network access controlled by MCP servers

### Configuration Security
- Schema validation prevents injection
- Version control for configuration changes
- Backup before migrations

## Performance Considerations

### Async Operations
- Parallel workflow execution for independent steps
- Non-blocking command execution
- Event bus uses async task scheduling

### Resource Management
- Event history limited to prevent memory growth
- Background tasks tracked and cancellable
- Connection pooling for external resources

### Caching
- Agent definitions cached on load
- Phase status cached between transitions
- Workflow state maintained in memory

## Future Architecture Evolution

### Phase 4: Security & Validation
- Tool abstraction layer for safe execution
- Input validation framework
- Sandboxed execution environment

### Long-term Vision
- Plugin architecture via entry_points
- GraphQL API for remote access
- Web UI for workflow visualization
- Agent marketplace for community contributions

## Design Patterns Used

1. **Event-Driven Architecture**: Loose coupling via event bus
2. **Command Pattern**: Encapsulated command execution
3. **Strategy Pattern**: Pluggable executors and migrations
4. **Observer Pattern**: Event subscriptions
5. **Factory Pattern**: Agent and workflow creation
6. **Repository Pattern**: Agent and phase management
7. **Middleware Pattern**: Event processing pipeline

## Technology Choices

- **Python 3.8+**: Modern async support, type hints
- **Dataclasses**: Immutable data structures
- **AsyncIO**: Native async/await support
- **YAML**: Human-readable configuration
- **JSON Schema**: Configuration validation
- **Rich/Click**: Terminal UI and CLI

## Conclusion

The Unified Agent System architecture provides a flexible, extensible foundation for AI-assisted software development. By combining event-driven design with careful separation of concerns, the system can evolve to meet future needs while maintaining backward compatibility and operational stability.