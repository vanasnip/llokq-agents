# Phase 2 Safety Features

## Overview

In response to PR review concerns, we've added comprehensive safety features to the workflow orchestration system to prevent "runaway agent" scenarios and ensure user control.

## Implemented Safety Features

### 1. Workflow-Level Approval

Workflows can now require approval before starting:

```json
{
  "name": "ua_workflow_start",
  "arguments": {
    "template": "feature_development",
    "inputs": {...},
    "require_approval": true
  }
}
```

If agents aren't pre-approved, the workflow returns:
```json
{
  "workflow_id": "wf_123",
  "status": "pending_approval",
  "agents_required": ["backend", "qa", "architect"],
  "agents_unapproved": ["backend", "qa"],
  "message": "Workflow requires approval for agents: backend, qa"
}
```

### 2. Resource Limits

The WorkflowEngine now enforces:
- **Max concurrent workflows**: Default 5
- **Workflow timeout**: Default 3600 seconds (1 hour)
- **Memory limits**: Default 512MB per workflow
- **CPU monitoring**: Via ResourceMonitor class

```python
WorkflowEngine(
    agent_registry=agents,
    context_manager=context,
    max_concurrent_workflows=5,
    workflow_timeout_seconds=3600,
    max_workflow_memory_mb=512
)
```

### 3. Workflow Cancellation

New tool `ua_workflow_cancel` allows stopping runaway workflows:

```json
{
  "name": "ua_workflow_cancel",
  "arguments": {
    "workflow_id": "wf_123",
    "reason": "User requested cancellation"
  }
}
```

Features:
- Graceful shutdown of running steps
- Resource cleanup
- Cancellation reason tracking

### 4. Dry Run Capability

Preview workflows before execution with `ua_workflow_dry_run`:

```json
{
  "name": "ua_workflow_dry_run",
  "arguments": {
    "template": "feature_development",
    "inputs": {"requirements": "Auth system"}
  }
}
```

Returns comprehensive analysis:
- Agents that would be used
- Step-by-step breakdown
- Resource estimates
- Missing inputs detection

### 5. Integration with Phase 1.2

The workflow approval system integrates with existing agent approval:
- Respects `SessionState.approved_agents`
- Honors `auto_approve` preferences
- Checks `block_agents` list

### 6. Resource Monitoring

The `ResourceMonitor` class provides:
- Memory usage tracking per workflow
- CPU usage monitoring
- Active workflow counting
- Graceful degradation if psutil unavailable

## Usage Examples

### Example 1: Workflow with Approval

```python
# User hasn't approved any agents yet
workflow_start("feature_development", require_approval=True)
# Returns: "pending_approval" with list of needed agents

# User approves agents
approve_agents(["backend", "qa", "architect"])

# Workflow can now start
workflow_start("feature_development", require_approval=True)
# Returns: workflow_id
```

### Example 2: Resource Limit Protection

```python
# Start 5 workflows (hits limit)
for i in range(5):
    workflow_start("api_design", {"resource": f"API_{i}"})

# 6th workflow blocked
workflow_start("api_design", {"resource": "API_6"})
# Error: "Maximum concurrent workflows (5) reached"
```

### Example 3: Safe Exploration with Dry Run

```python
# Preview without execution
dry_run("security_audit", {"scope": "entire_system"})
# Returns: agents needed, steps, resource estimates

# User sees it needs 5 agents and 500MB memory
# Can decide whether to proceed
```

## Implementation Details

### Approval Flow
1. Check if `require_approval` or `!auto_approve`
2. Extract agents from workflow template
3. Compare with approved agents
4. Return pending status if unapproved agents found
5. Otherwise proceed with execution

### Resource Enforcement
1. Count active workflows before starting new ones
2. Monitor memory usage per step
3. Check cancellation status between steps
4. Clean up resources on completion/failure

### Error Handling
- Workflow failures tracked with error messages
- Resource cleanup on all exit paths
- Proper status updates (FAILED, CANCELLED, COMPLETED)

## Testing

Comprehensive test suite (`test_workflow_safety.py`) validates:
- ✅ Dry run analysis
- ✅ Approval requirements
- ✅ Agent approval flow
- ✅ Workflow cancellation
- ✅ Resource limits
- ✅ Auto-approval preferences

## Future Enhancements

1. **Checkpointing**: Save workflow state for resume
2. **Rate Limiting**: Per-agent execution limits
3. **Cost Tracking**: Estimate and track resource costs
4. **Workflow Policies**: Admin-defined safety rules
5. **Audit Logging**: Detailed execution history

## Conclusion

These safety features address the PR review concerns by ensuring:
- No workflows run without user awareness
- Resource usage is bounded
- Runaway workflows can be stopped
- Users can preview before execution
- Existing approval mechanisms are respected

The implementation maintains the power of workflow orchestration while adding crucial safety rails for production use.