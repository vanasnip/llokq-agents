# Phase 1.2: User Control Mechanisms

## Overview

Implement user control tools that enable Claude to suggest agents while giving users full control over which agents are activated.

## Architecture Design

### Session State Management

Since MCP servers are stateless by design, we need to handle session state carefully:

```python
class SessionState:
    """Manages user preferences and approvals"""
    def __init__(self):
        self.approved_agents = set()  # Agents approved for this session
        self.rejected_agents = set()  # Explicitly rejected agents
        self.auto_approve = False     # Auto-approve all suggestions
        self.last_suggestion = None   # Track last suggestion for approval
```

### Control Flow

```
1. User describes task
2. Claude calls ua_suggest_agents
3. Server analyzes task and suggests agents
4. Claude presents suggestions to user
5. User approves/rejects via ua_approve_agents
6. Claude proceeds with approved agents only
```

## Tools to Implement

### 1. ua_suggest_agents

**Purpose**: Analyze a task and suggest appropriate agents

**Input**:
- `task` (string): Description of what the user wants to accomplish
- `context` (optional): Additional context about the project

**Output**:
- Suggested agents with rationale
- Confidence scores
- Suggestion ID for approval tracking

**Logic**:
- Parse task for keywords
- Match against agent capabilities
- Consider agent compatibility
- Return ranked suggestions

### 2. ua_approve_agents

**Purpose**: Handle user approval/rejection of agent suggestions

**Input**:
- `action` (enum): "approve", "reject", "approve_all", "reset"
- `agents` (array): Agent IDs to approve/reject
- `suggestion_id` (optional): Reference to specific suggestion

**Output**:
- Updated approval status
- List of currently approved agents
- Session preferences

### 3. ua_set_preferences

**Purpose**: Configure session-wide preferences

**Input**:
- `auto_approve` (boolean): Auto-approve all suggestions
- `require_approval` (array): Agents that always need approval
- `block_agents` (array): Agents to never use

**Output**:
- Updated preferences
- Current session state

## Implementation Details

### Task Analysis

```python
def analyze_task(task: str) -> List[Tuple[str, float, str]]:
    """
    Analyze task and return (agent_id, confidence, reason) tuples
    """
    suggestions = []
    task_lower = task.lower()
    
    # Keywords for each agent
    qa_keywords = ["test", "quality", "bug", "coverage", "validation"]
    backend_keywords = ["api", "database", "server", "endpoint", "backend"]
    architect_keywords = ["design", "architecture", "system", "structure", "scale"]
    
    # Score each agent
    for agent_id, keywords in [...]:
        score = calculate_relevance(task_lower, keywords)
        if score > threshold:
            suggestions.append((agent_id, score, reason))
    
    return sorted(suggestions, key=lambda x: x[1], reverse=True)
```

### Approval Tracking

Since MCP is stateless, we'll use a simple in-memory approach:
- Generate suggestion IDs
- Track approvals by suggestion ID
- Clear old suggestions periodically

## Example Interactions

### Basic Flow

```
User: "I need to build a REST API for user management"

Claude: [calls ua_suggest_agents with task]

Response: 
{
  "suggestion_id": "sug_123",
  "suggestions": [
    {
      "agent": "backend",
      "confidence": 0.95,
      "reason": "REST API and database expertise"
    },
    {
      "agent": "architect",
      "confidence": 0.75,
      "reason": "System design for scalability"
    },
    {
      "agent": "qa",
      "confidence": 0.70,
      "reason": "API testing and validation"
    }
  ]
}

Claude: "I suggest using the Backend Agent (95% match) for REST API development, 
        Architect (75%) for system design, and QA Agent (70%) for testing.
        Would you like to use these agents?"

User: "Just backend and qa"

Claude: [calls ua_approve_agents with agents=["backend", "qa"]]

Response:
{
  "approved": ["backend", "qa"],
  "rejected": ["architect"],
  "session_status": {
    "auto_approve": false,
    "total_approved": 2
  }
}
```

### Auto-Approval

```
User: "Auto-approve all agent suggestions for this session"

Claude: [calls ua_set_preferences with auto_approve=true]

User: "Help me optimize database queries"

Claude: [calls ua_suggest_agents]
        [Automatically proceeds with suggested agents]
```

## Testing Plan

1. Test suggestion quality for various tasks
2. Verify approval/rejection tracking
3. Test session preferences
4. Ensure stateless operation
5. Test edge cases (empty suggestions, invalid agents)

## Success Metrics

- Relevant agent suggestions (>80% accuracy)
- Smooth approval flow
- Clear user control
- No surprise agent activations