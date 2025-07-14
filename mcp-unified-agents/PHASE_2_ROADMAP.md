# Phase 2 Implementation Roadmap

## Overview

This roadmap outlines the implementation steps for Phase 2's unified architecture, focusing on workflow orchestration and context sharing.

## Implementation Phases

### Phase 2.1: Core Workflow Engine (Week 1)

#### Day 1-2: Workflow Infrastructure
- [ ] Create WorkflowEngine class
- [ ] Implement WorkflowExecution state management
- [ ] Add workflow ID generation and tracking
- [ ] Build step execution framework

#### Day 3-4: Template System
- [ ] Create TemplateRegistry class
- [ ] Implement template validation
- [ ] Add template loading from YAML/JSON
- [ ] Build input resolution system

#### Day 5: Integration
- [ ] Wire workflow engine into MCP server
- [ ] Add workflow tools to tool registry
- [ ] Test basic workflow execution
- [ ] Handle errors and rollbacks

### Phase 2.2: Context Sharing (Week 2)

#### Day 1-2: Context Manager
- [ ] Implement SharedContext class
- [ ] Create ContextManager with access control
- [ ] Add artifact storage and retrieval
- [ ] Implement context expiration

#### Day 3-4: Agent Integration
- [ ] Modify agent tools to use shared context
- [ ] Add context-aware tool execution
- [ ] Implement artifact permissions
- [ ] Test cross-agent data sharing

#### Day 5: Optimization
- [ ] Add context compression for large artifacts
- [ ] Implement memory limits
- [ ] Create context cleanup scheduler
- [ ] Performance benchmarking

### Phase 2.3: Workflow Templates (Week 3)

#### Day 1-2: Core Templates
- [ ] Implement feature_development template
- [ ] Create bug_fix template
- [ ] Add security_audit template
- [ ] Build api_design template

#### Day 3-4: Advanced Features
- [ ] Add parallel step execution
- [ ] Implement conditional branching
- [ ] Create loop constructs
- [ ] Add error recovery steps

#### Day 5: User Features
- [ ] Build custom workflow creator
- [ ] Add workflow modification UI
- [ ] Implement workflow favorites
- [ ] Create workflow analytics

## File Structure

```
mcp-unified-agents/
├── server.py                    # Enhanced with workflow support
├── workflow/
│   ├── __init__.py
│   ├── engine.py               # WorkflowEngine implementation
│   ├── templates.py            # TemplateRegistry
│   ├── context.py              # Context management
│   └── executor.py             # Step execution logic
├── templates/
│   ├── feature_development.yaml
│   ├── bug_fix.yaml
│   ├── security_audit.yaml
│   └── api_design.yaml
├── tests/
│   ├── test_workflow_engine.py
│   ├── test_context_sharing.py
│   └── test_templates.py
└── docs/
    ├── workflow_guide.md
    └── template_authoring.md
```

## Code Implementation Plan

### 1. Extend server.py

```python
# Add to server.py
from workflow.engine import WorkflowEngine
from workflow.context import ContextManager

class UnifiedAgentServer:
    def __init__(self):
        # ... existing init ...
        self.context_manager = ContextManager()
        self.workflow_engine = WorkflowEngine(
            agent_registry=self.agents,
            context_manager=self.context_manager
        )
        
    def _handle_call_tool(self, tool_name: str, arguments: Dict) -> Dict:
        # ... existing routing ...
        elif tool_name.startswith('ua_workflow_'):
            return self._handle_workflow_tool(tool_name, arguments)
        elif tool_name.startswith('ua_context_'):
            return self._handle_context_tool(tool_name, arguments)
```

### 2. Create workflow/engine.py

```python
# workflow/engine.py
import uuid
from typing import Dict, Any, List
from datetime import datetime
from .templates import TemplateRegistry
from .context import SharedContext
from .executor import StepExecutor

class WorkflowEngine:
    def __init__(self, agent_registry, context_manager):
        self.agents = agent_registry
        self.context_manager = context_manager
        self.template_registry = TemplateRegistry()
        self.step_executor = StepExecutor(agent_registry)
        self.active_workflows = {}
        
    def start_workflow(self, template_name: str, inputs: Dict) -> str:
        """Initialize and start a workflow"""
        workflow_id = str(uuid.uuid4())
        template = self.template_registry.get_template(template_name)
        
        workflow = {
            'id': workflow_id,
            'template': template_name,
            'status': 'running',
            'current_step': 0,
            'inputs': inputs,
            'context': SharedContext(),
            'started_at': datetime.now(),
            'steps_completed': [],
            'artifacts': {}
        }
        
        self.active_workflows[workflow_id] = workflow
        return workflow_id
```

### 3. Create workflow/context.py

```python
# workflow/context.py
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

class SharedContext:
    """Manages shared state within a workflow"""
    
    def __init__(self):
        self.artifacts = {}
        self.insights = {}
        self.constraints = []
        self.agent_states = {}
        self._access_log = []
        
    def add_artifact(self, key: str, value: Any, 
                    producer: str, consumers: List[str] = None):
        """Add an artifact to shared context"""
        self.artifacts[key] = {
            'value': value,
            'producer': producer,
            'consumers': consumers or ['*'],
            'created_at': datetime.now(),
            'accessed_by': []
        }
        
    def get_artifact(self, key: str, consumer: str) -> Optional[Any]:
        """Retrieve artifact with access control"""
        if key not in self.artifacts:
            return None
            
        artifact = self.artifacts[key]
        
        # Check access permissions
        if '*' not in artifact['consumers'] and consumer not in artifact['consumers']:
            raise PermissionError(f"Agent {consumer} not authorized for {key}")
            
        # Log access
        artifact['accessed_by'].append({
            'agent': consumer,
            'timestamp': datetime.now()
        })
        
        return artifact['value']
```

### 4. Create workflow/templates.py

```python
# workflow/templates.py
import yaml
from pathlib import Path
from typing import Dict, List

class TemplateRegistry:
    """Manages workflow templates"""
    
    def __init__(self):
        self.templates = {}
        self._load_builtin_templates()
        
    def _load_builtin_templates(self):
        """Load templates from templates/ directory"""
        template_dir = Path(__file__).parent.parent / 'templates'
        
        for template_file in template_dir.glob('*.yaml'):
            with open(template_file) as f:
                template = yaml.safe_load(f)
                self.templates[template['id']] = template
                
    def register_custom_template(self, template: Dict):
        """Register a user-defined template"""
        self._validate_template(template)
        self.templates[template['id']] = template
        
    def _validate_template(self, template: Dict):
        """Validate template structure"""
        required_fields = ['id', 'name', 'description', 'steps']
        for field in required_fields:
            if field not in template:
                raise ValueError(f"Template missing required field: {field}")
```

## Testing Plan

### Unit Tests

```python
# tests/test_workflow_engine.py
def test_workflow_creation():
    """Test workflow initialization"""
    engine = WorkflowEngine(mock_agents, mock_context)
    workflow_id = engine.start_workflow('feature_development', {
        'requirements': 'Add auth system'
    })
    
    assert workflow_id in engine.active_workflows
    assert engine.active_workflows[workflow_id]['status'] == 'running'

def test_step_execution():
    """Test individual step execution"""
    engine = WorkflowEngine(mock_agents, mock_context)
    result = engine.execute_step(workflow_id, {
        'agent': 'architect',
        'tool': 'ua_architect_design',
        'input': {'requirements': 'Auth system'}
    })
    
    assert result is not None
    assert 'design' in result
```

### Integration Tests

```python
# tests/test_integration.py
def test_full_workflow():
    """Test complete workflow execution"""
    server = UnifiedAgentServer()
    
    # Start workflow
    response = server.handle_request({
        'method': 'tools/call',
        'params': {
            'name': 'ua_workflow_start',
            'arguments': {
                'template': 'bug_fix',
                'inputs': {'bug_description': 'Login fails'}
            }
        }
    })
    
    workflow_id = response['result']['workflow_id']
    
    # Check status
    status = server.handle_request({
        'method': 'tools/call',
        'params': {
            'name': 'ua_workflow_status',
            'arguments': {'workflow_id': workflow_id}
        }
    })
    
    assert status['result']['status'] == 'completed'
```

## Deployment Strategy

### 1. Feature Flags
```python
FEATURES = {
    'workflows_enabled': False,
    'context_sharing_enabled': False,
    'custom_workflows_enabled': False
}
```

### 2. Gradual Rollout
- Week 1: Internal testing with core team
- Week 2: Beta users with feature flag
- Week 3: General availability
- Week 4: Custom workflows enabled

### 3. Monitoring
```python
class WorkflowMetrics:
    def track_workflow_start(self, template: str):
        # Track workflow usage
        
    def track_completion_time(self, workflow_id: str, duration: float):
        # Track performance
        
    def track_failure(self, workflow_id: str, error: str):
        # Track errors
```

## Documentation Plan

### 1. User Guide
- Getting started with workflows
- Available workflow templates
- Creating custom workflows
- Best practices

### 2. Developer Guide
- Template authoring
- Custom agent integration
- Context sharing patterns
- Performance optimization

### 3. API Reference
- Workflow tools documentation
- Context tools documentation
- Template schema reference
- Error handling guide

## Risk Mitigation

### 1. Performance Risks
- **Risk**: Large contexts causing memory issues
- **Mitigation**: Implement size limits and compression

### 2. Complexity Risks
- **Risk**: Workflows too complex for users
- **Mitigation**: Start with simple templates, gather feedback

### 3. Integration Risks
- **Risk**: Breaking existing functionality
- **Mitigation**: Comprehensive test suite, feature flags

## Success Criteria

### Week 1 Goals
- [ ] Basic workflow execution working
- [ ] 3 unit tests passing
- [ ] No regression in existing tools

### Week 2 Goals
- [ ] Context sharing operational
- [ ] 2 workflow templates complete
- [ ] Integration tests passing

### Week 3 Goals
- [ ] All 4 core templates implemented
- [ ] Custom workflow creation working
- [ ] Documentation complete

## Next Actions

1. Create workflow/ directory structure
2. Implement WorkflowEngine class
3. Write unit tests for engine
4. Create first workflow template
5. Test with simple workflow

This roadmap provides a clear path from Phase 1's foundation to Phase 2's intelligent orchestration capabilities.