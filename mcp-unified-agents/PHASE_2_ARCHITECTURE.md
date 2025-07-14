# Phase 2: Unified Architecture Design

## Overview

Phase 2 focuses on creating an intelligent orchestration layer that enables multi-agent collaboration through workflow templates and context sharing. This builds on the foundation of Phase 1's discovery and control mechanisms.

## Architecture Components

### 1. Workflow Engine

The workflow engine orchestrates multi-agent collaboration patterns discovered through Phase 1 usage.

```
┌─────────────────────────────────────────────────┐
│                 Workflow Engine                  │
├─────────────────────────────────────────────────┤
│  Template Registry    │    Execution Context    │
│  ┌─────────────────┐ │  ┌──────────────────┐  │
│  │ Feature Dev     │ │  │ Current Step     │  │
│  │ Bug Fix         │ │  │ Agent States     │  │
│  │ Security Audit  │ │  │ Shared Memory    │  │
│  │ API Design      │ │  │ Results Cache    │  │
│  │ Custom...       │ │  │ User Preferences │  │
│  └─────────────────┘ │  └──────────────────┘  │
└─────────────────────────────────────────────────┘
```

### 2. Context Sharing System

Enables agents to build on each other's work without redundant analysis.

```python
class SharedContext:
    """Manages shared state between agents"""
    
    def __init__(self):
        self.artifacts = {}      # Shared outputs
        self.insights = {}       # Agent discoveries
        self.constraints = []    # Project constraints
        self.preferences = {}    # User preferences
        self.history = []        # Execution history
```

### 3. Workflow Templates

Based on common patterns observed in Phase 1:

#### Feature Development Template
```yaml
templates:
  feature_development:
    name: "Feature Development Workflow"
    description: "End-to-end feature implementation"
    steps:
      - agent: architect
        tool: ua_architect_design
        input: "{requirements}"
        output: architecture_design
        
      - agent: backend
        tool: ua_backend_api_design
        input: 
          requirements: "{requirements}"
          architecture: "{architecture_design}"
        output: api_spec
        
      - agent: qa
        tool: ua_qa_test_generate
        input:
          feature: "{requirements}"
          api_spec: "{api_spec}"
        output: test_plan
        
      - parallel:
        - agent: backend
          tool: ua_backend_implement
          input: "{api_spec}"
          output: backend_code
          
        - agent: frontend
          tool: ua_frontend_implement
          input: "{api_spec}"
          output: frontend_code
          
      - agent: qa
        tool: ua_qa_test_execute
        input:
          test_plan: "{test_plan}"
          code: ["{backend_code}", "{frontend_code}"]
        output: test_results
```

#### Bug Fix Template
```yaml
templates:
  bug_fix:
    name: "Bug Fix Workflow"
    description: "Systematic bug resolution"
    steps:
      - agent: qa
        tool: ua_qa_analyze_bug
        input: "{bug_description}"
        output: root_cause
        
      - agent: backend
        tool: ua_backend_debug
        input: "{root_cause}"
        output: fix_plan
        
      - agent: backend
        tool: ua_backend_implement_fix
        input: "{fix_plan}"
        output: fix_code
        
      - agent: qa
        tool: ua_qa_verify_fix
        input:
          bug: "{bug_description}"
          fix: "{fix_code}"
        output: verification
```

### 4. Advanced Tool Categories

#### Workflow Management Tools
```python
workflow_tools = [
    {
        "name": "ua_workflow_start",
        "description": "Start a workflow template",
        "parameters": {
            "template": "string",
            "inputs": "object",
            "options": {
                "interactive": "boolean",
                "auto_approve": "boolean"
            }
        }
    },
    {
        "name": "ua_workflow_status",
        "description": "Get workflow execution status",
        "parameters": {
            "workflow_id": "string"
        }
    },
    {
        "name": "ua_workflow_customize",
        "description": "Create custom workflow",
        "parameters": {
            "name": "string",
            "steps": "array"
        }
    }
]
```

#### Context Tools
```python
context_tools = [
    {
        "name": "ua_context_share",
        "description": "Share artifact between agents",
        "parameters": {
            "key": "string",
            "value": "any",
            "agents": "array[string]"
        }
    },
    {
        "name": "ua_context_retrieve",
        "description": "Retrieve shared context",
        "parameters": {
            "key": "string",
            "agent": "string"
        }
    }
]
```

## Implementation Details

### 1. Workflow Execution Engine

```python
class WorkflowEngine:
    def __init__(self, agent_registry, context_manager):
        self.templates = self._load_templates()
        self.agents = agent_registry
        self.context = context_manager
        self.executions = {}
        
    def start_workflow(self, template_name: str, inputs: Dict) -> str:
        """Start a workflow execution"""
        workflow_id = self._generate_id()
        template = self.templates[template_name]
        
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            template=template,
            inputs=inputs,
            context=SharedContext()
        )
        
        self.executions[workflow_id] = execution
        return workflow_id
        
    def execute_step(self, workflow_id: str, step: Dict) -> Any:
        """Execute a single workflow step"""
        execution = self.executions[workflow_id]
        
        # Handle parallel execution
        if "parallel" in step:
            return self._execute_parallel(execution, step["parallel"])
            
        # Single step execution
        agent = self.agents[step["agent"]]
        tool = step["tool"]
        inputs = self._resolve_inputs(step["input"], execution.context)
        
        result = agent.execute_tool(tool, inputs)
        
        # Store output in context
        if "output" in step:
            execution.context.artifacts[step["output"]] = result
            
        return result
```

### 2. Context Manager

```python
class ContextManager:
    def __init__(self):
        self.global_context = {}
        self.workflow_contexts = {}
        
    def share_artifact(self, workflow_id: str, key: str, value: Any, 
                      agents: List[str] = None):
        """Share an artifact within workflow context"""
        if workflow_id not in self.workflow_contexts:
            self.workflow_contexts[workflow_id] = SharedContext()
            
        context = self.workflow_contexts[workflow_id]
        context.artifacts[key] = {
            "value": value,
            "shared_with": agents or "all",
            "timestamp": datetime.now()
        }
        
    def get_artifact(self, workflow_id: str, key: str, agent: str) -> Any:
        """Retrieve shared artifact with access control"""
        context = self.workflow_contexts.get(workflow_id)
        if not context:
            return None
            
        artifact = context.artifacts.get(key)
        if not artifact:
            return None
            
        # Check access permissions
        if artifact["shared_with"] != "all" and agent not in artifact["shared_with"]:
            raise PermissionError(f"Agent {agent} not authorized for {key}")
            
        return artifact["value"]
```

### 3. Template Registry

```python
class TemplateRegistry:
    def __init__(self):
        self.templates = self._load_builtin_templates()
        self.custom_templates = {}
        
    def register_template(self, name: str, template: Dict):
        """Register a custom workflow template"""
        # Validate template structure
        self._validate_template(template)
        
        self.custom_templates[name] = template
        
    def get_template(self, name: str) -> Dict:
        """Get template by name"""
        if name in self.custom_templates:
            return self.custom_templates[name]
        return self.templates.get(name)
        
    def _validate_template(self, template: Dict):
        """Validate template structure"""
        required = ["name", "description", "steps"]
        for field in required:
            if field not in template:
                raise ValueError(f"Template missing required field: {field}")
```

## Integration with Phase 1

### Enhanced Discovery
```python
def ua_agent_suggest_workflow(task: str) -> Dict:
    """Suggest both agents and workflows for a task"""
    # Use Phase 1 agent suggestion
    agents = suggest_agents(task)
    
    # Also suggest relevant workflows
    workflows = []
    
    if "feature" in task.lower() or "implement" in task.lower():
        workflows.append({
            "template": "feature_development",
            "confidence": 0.85,
            "reason": "Full feature development cycle"
        })
        
    if "bug" in task.lower() or "fix" in task.lower():
        workflows.append({
            "template": "bug_fix",
            "confidence": 0.90,
            "reason": "Systematic bug resolution"
        })
        
    return {
        "agents": agents,
        "workflows": workflows
    }
```

### Workflow Approval Flow
```python
def ua_workflow_approve(workflow_id: str, action: str) -> Dict:
    """Approve/reject workflow execution"""
    if action == "approve":
        # Continue workflow execution
        engine.continue_workflow(workflow_id)
    elif action == "modify":
        # Allow step customization
        return {"status": "awaiting_modifications"}
    elif action == "cancel":
        # Cancel workflow
        engine.cancel_workflow(workflow_id)
```

## Usage Examples

### Example 1: Feature Development
```
User: "I need to add user authentication to the API"

Claude: I suggest using the Feature Development workflow with these agents:
- Architect: System design for auth
- Backend: API implementation
- Security: Auth security review
- QA: Testing auth flows

[Approve workflow? (y)es / (m)odify / (n)o]

User: y

Claude: Starting Feature Development workflow...

[Step 1/5] Architect designing authentication system...
✓ Designed JWT-based auth with refresh tokens

[Step 2/5] Backend designing auth API endpoints...
✓ Created REST API spec for /auth/login, /auth/refresh, /auth/logout

[Step 3/5] QA generating test plan...
✓ Generated 15 test cases covering auth flows

[Step 4/5] Parallel execution:
  - Backend implementing auth service...
  - Frontend implementing auth UI...
✓ Implementation complete

[Step 5/5] QA executing tests...
✓ All tests passing

Workflow complete! Auth system implemented with:
- JWT token management
- Secure password hashing
- Rate limiting
- Comprehensive test coverage
```

### Example 2: Custom Workflow
```
User: "Create a custom workflow for database migrations"

Claude: I'll help you create a custom workflow. What steps should it include?

User: "First analyze the schema changes, then generate migration scripts, test them, and create rollback plans"

Claude: [calls ua_workflow_customize]

Created custom workflow "Database Migration":
1. Data Agent: Analyze schema changes
2. Backend Agent: Generate migration scripts
3. QA Agent: Test migrations on staging
4. Backend Agent: Create rollback scripts
5. DevOps Agent: Prepare deployment plan

Would you like to run this workflow now?
```

## Performance Considerations

### 1. Context Size Management
- Implement artifact expiration
- Compress large artifacts
- Limit context history depth

### 2. Parallel Execution
- Use asyncio for true parallelism
- Implement step dependency resolution
- Handle partial failures gracefully

### 3. Memory Optimization
```python
class ContextCleaner:
    def clean_expired_artifacts(self, context: SharedContext):
        """Remove expired artifacts to prevent memory bloat"""
        current_time = datetime.now()
        expired_keys = [
            key for key, artifact in context.artifacts.items()
            if current_time - artifact["timestamp"] > timedelta(hours=1)
        ]
        for key in expired_keys:
            del context.artifacts[key]
```

## Testing Strategy

### 1. Workflow Template Tests
```python
def test_feature_workflow():
    """Test complete feature development workflow"""
    engine = WorkflowEngine()
    
    workflow_id = engine.start_workflow(
        "feature_development",
        {"requirements": "Add user authentication"}
    )
    
    # Verify each step executes correctly
    status = engine.get_status(workflow_id)
    assert status["completed_steps"] == 5
    assert status["status"] == "completed"
```

### 2. Context Sharing Tests
```python
def test_context_sharing():
    """Test artifact sharing between agents"""
    context = ContextManager()
    
    # Backend shares API spec
    context.share_artifact(
        "wf_123", 
        "api_spec",
        {"endpoints": ["/auth/login"]},
        ["frontend", "qa"]
    )
    
    # Frontend retrieves it
    spec = context.get_artifact("wf_123", "api_spec", "frontend")
    assert spec["endpoints"] == ["/auth/login"]
    
    # Unauthorized agent blocked
    with pytest.raises(PermissionError):
        context.get_artifact("wf_123", "api_spec", "devops")
```

## Success Metrics

1. **Workflow Completion Rate**: >85% workflows complete successfully
2. **Context Reuse**: >60% of artifacts shared between agents
3. **Time Savings**: 40% reduction in multi-agent task time
4. **User Satisfaction**: Workflow suggestions accepted >75%

## Migration Path

### From Phase 1 to Phase 2
1. Retain all Phase 1 tools
2. Add workflow tools alongside
3. Gradually introduce workflows for common patterns
4. Allow fallback to individual agent calls

## Next Steps

1. Implement WorkflowEngine class
2. Create 3-5 core workflow templates
3. Build context sharing system
4. Add workflow discovery tools
5. Test with real-world scenarios
6. Iterate based on usage patterns

## Conclusion

Phase 2 transforms the MCP server from a collection of independent agents into an intelligent orchestration platform. By introducing workflows and context sharing, we enable sophisticated multi-agent collaboration while maintaining user control and transparency.