# Technical Review Action Plan - Unified Agent System

*Based on LLOKQ Technical Review v0.1 - July 13, 2025*

## Comprehensive Plan to Address Technical Review Feedback

### 1. **Architecture & Domain Model Fixes**

#### Fix Hard-coded Enums and Type Issues
- **Convert AgentCategory enum to a registry pattern** to allow dynamic agent types
- **Fix risk_profile to use RiskProfile enum** instead of string (line 38 in schema.py)
- **Create plugin architecture** using entry_points for extensible agent categories

#### Fix Import Path Issues
- **Remove fallback import** in cli.py line 25 that tries `from agents.manager import`
- **Standardize all imports** to use the package path `unified.agents`

#### Implement Event Bus for Activation
- **Create EventBus class** to handle agent activation/deactivation events
- **Refactor PhaseManager and CommandParser** to publish events instead of direct manipulation
- **AgentManager subscribes** to events and maintains single source of truth

#### Add Real Parallel Execution
- **Implement AsyncWorkflowEngine** using asyncio
- **Add async execute methods** in CommandExecutor
- **Use asyncio.gather()** for parallel step execution

### 2. **Testing Infrastructure**

#### Create Test Suite Structure
```
tests/
├── unit/
│   ├── test_agent_schema.py
│   ├── test_command_parser.py
│   ├── test_workflow_engine.py
│   └── test_phase_manager.py
├── integration/
│   ├── test_cli_interactive.py
│   └── test_workflow_execution.py
└── conftest.py
```

#### Key Test Coverage
- **Parser round-trip tests** for all command patterns
- **CLI integration tests** using pexpect
- **Type checking** with mypy
- **Schema validation tests**
- **Event bus message flow tests**

### 3. **Security & Validation**

#### Schema Versioning
- **Add schema_version field** to all YAML configs
- **Create migration framework** for config upgrades
- **Implement SchemaValidator** using pydantic or marshmallow

#### Secure Execution
- **Create Tool abstraction base class** with dry_run() and execute()
- **Implement sandboxed execution** using Docker SDK
- **Add input validation** for all command parameters

### 4. **CI/CD Pipeline**

#### GitHub Actions Workflow
```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11, 3.12]
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          pip install -e .[dev]
      - name: Lint with ruff
        run: ruff check .
      - name: Type check with mypy
        run: mypy unified/
      - name: Test with pytest
        run: pytest --cov=unified --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### 5. **Documentation Restructure**

#### Split Documentation
- **README.md** - Brief overview with animated GIF demo
- **docs/getting-started.md** - Installation and quick start
- **docs/architecture.md** - Design philosophy and patterns
- **docs/agent-authoring.md** - How to create custom agents
- **docs/api-reference.md** - Generated from docstrings

### 6. **Package & Config Improvements**

#### Dynamic Agent Loading
- **Implement plugin discovery** via entry_points
- **Add project-local config** support (./agents.yml overrides ~/.claude/agents.yml)
- **Create config merge strategy** with clear precedence rules

#### Version Management
- **Add __version__** to package
- **Include version in CLI --version output**
- **Tag releases with semantic versioning**

### 7. **Short-term Implementation (Week 1-2)**

1. **Fix critical bugs**:
   - Import path issues
   - risk_profile type fix
   - Add __version__ = "0.1.1"

2. **Add minimal test suite**:
   - Basic pytest setup
   - Command parser tests
   - GitHub Actions CI

3. **Implement async stub**:
   - AsyncWorkflowEngine skeleton
   - Mark parallel steps for future implementation

### 8. **Medium-term Goals (Month 1)**

1. **Event bus architecture**
2. **Plugin system via entry_points**
3. **Schema versioning and migration**
4. **Docker-based sandboxed execution**
5. **Comprehensive test coverage (>80%)**

### 9. **Long-term Vision (Quarter 1)**

1. **GraphQL API** for remote workflow triggering
2. **Web UI** for workflow visualization
3. **Agent marketplace** for community contributions
4. **Self-testing agents** with capability audits

## Implementation Priority Order

### Phase 1: Critical Fixes (Immediate)
1. Fix import paths (cli.py line 25)
2. Fix risk_profile type (schema.py line 38)
3. Add version info
4. Create basic test structure

### Phase 2: Testing & CI (Week 1)
1. Set up pytest and basic tests
2. Add GitHub Actions workflow
3. Configure mypy and ruff
4. Add coverage reporting

### Phase 3: Architecture Improvements (Week 2)
1. Implement event bus pattern
2. Create async workflow stubs
3. Add schema versioning
4. Document architecture decisions

### Phase 4: Security & Validation (Month 1)
1. Implement Tool abstraction
2. Add input validation
3. Create sandboxed execution
4. Schema migration framework

## Success Metrics

- **Code Quality**: >80% test coverage, zero mypy errors
- **Performance**: Parallel steps execute concurrently
- **Security**: All user inputs validated, execution sandboxed
- **Extensibility**: New agents can be added via plugins
- **Documentation**: All public APIs documented

## Open Questions to Address

1. **Licensing**: Clarify package name vs D3P-SuperClaude branding
2. **State Management**: Define concurrent workspace isolation strategy
3. **Execution Model**: Confirm advisory vs real execution requirements
4. **User Personas**: Document primary use cases (solo dev vs team CI)

This plan addresses all major concerns from the review while maintaining backward compatibility and setting up for sustainable growth.