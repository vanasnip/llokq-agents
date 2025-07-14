# Unified Agents MCP Server Plan

## Overview

Create a single MCP (Model Context Protocol) server that exposes all development agents (QA, Design, Development, Architecture, Operations) as tools for Claude Code, with user control over agent selection and the ability to discover agent capabilities.

## Key Features

1. **Single MCP Server** containing all agents (except git commands which remain as slash commands)
2. **User Control** over agent selection:
   - Approve individual agent suggestions
   - Approve all agents for session
   - Reject agents
   - Add additional agents to Claude's selection
3. **Manual Agent Invocation** - ability to explicitly call specific agents using @ notation
4. **Agent Discovery** - list agents and get detailed information about their capabilities

## Architecture

```
unified-agents-mcp-server/
├── agent-registry/
│   ├── design-agents/ (5 agents)
│   │   ├── riley (requirements)
│   │   ├── aura (accessibility)
│   │   ├── brand_maven (branding)
│   │   ├── layout_loom (layout)
│   │   └── ui (ui/ux)
│   ├── architecture-agents/ (2 agents)
│   │   ├── architect (system)
│   │   └── api (api design)
│   ├── development-agents/ (4 agents)
│   │   ├── backend
│   │   ├── frontend
│   │   ├── data
│   │   └── mobile
│   ├── qa-agents/ (3 agents)
│   │   ├── qa (testing)
│   │   ├── security
│   │   └── performance
│   └── operations-agents/ (1 agent)
│       └── devops
├── workflow-orchestration/
├── user-control/
└── agent-discovery/
```

## Tool Categories

### Agent Discovery Tools
- `ua_agent_list` - List all available agents with brief descriptions
- `ua_agent_info` - Get detailed information about a specific agent
- `ua_agent_capabilities` - Get agent's specific capabilities and preferences
- `ua_agent_compatible` - Find agents compatible with current agent
- `ua_agent_search` - Search agents by capability or domain

### Design Tools (ua_design_*)
- `ua_design_requirements_analyze` - Riley analyzes requirements
- `ua_design_ui_review` - UI/UX agent reviews interfaces
- `ua_design_accessibility_audit` - Aura checks accessibility
- `ua_design_brand_check` - Brand Maven ensures consistency
- `ua_design_layout_optimize` - Layout Loom improves structure

### Architecture Tools (ua_architect_*)
- `ua_architect_system_design` - Design system architecture
- `ua_architect_api_design` - Design API structure
- `ua_architect_pattern_suggest` - Suggest design patterns
- `ua_architect_review_structure` - Review code architecture
- `ua_architect_dependencies_analyze` - Analyze dependencies

### Development Tools (ua_dev_*)
- `ua_dev_backend_implement` - Backend implementation
- `ua_dev_frontend_implement` - Frontend implementation
- `ua_dev_database_design` - Data agent designs schemas
- `ua_dev_mobile_implement` - Mobile-specific implementation
- `ua_dev_code_review` - Multi-agent code review
- `ua_dev_refactor_suggest` - Suggest refactoring

### QA Tools (ua_qa_*)
- `ua_qa_test_generate` - Generate test cases
- `ua_qa_coverage_analyze` - Analyze test coverage
- `ua_qa_security_audit` - Security testing
- `ua_qa_performance_test` - Performance testing
- `ua_qa_bug_analyze` - Bug root cause analysis

### Operations Tools (ua_ops_*)
- `ua_ops_deployment_plan` - Plan deployment strategy
- `ua_ops_dockerfile_generate` - Create Dockerfiles
- `ua_ops_ci_setup` - Setup CI/CD pipelines
- `ua_ops_monitoring_setup` - Setup monitoring
- `ua_ops_incident_analyze` - Analyze incidents

### Workflow Tools (ua_workflow_*)
- `ua_workflow_feature` - Run feature development workflow
- `ua_workflow_bug` - Run bug fix workflow
- `ua_workflow_security` - Run security audit workflow
- `ua_workflow_deployment` - Run deployment workflow
- `ua_workflow_custom` - Run custom workflow

### Meta Tools (User Control)
- `ua_agent_suggest` - Claude proposes agents for task
- `ua_agent_approve` - User approves agent selection
- `ua_agent_add` - User adds agents to selection
- `ua_agent_session_preferences` - Set session-wide preferences

## User Interaction Patterns

### 1. Agent Discovery

```
User: "@agents"

Claude: Here are all available agents:

**Design Agents:**
- riley: Requirements Detective | Uncovers hidden needs
- aura: Accessibility Advocate | Ensures universal access
- brand_maven: Brand Guardian | Maintains visual consistency
- layout_loom: Layout Architect | Optimizes spatial design
- ui: UI/UX Designer | Creates intuitive interfaces

**Architecture Agents:**
- architect: System Architect | Designs scalable systems
- api: API Designer | Creates elegant interfaces

**Development Agents:**
- backend: Backend Engineer | Builds robust services
- frontend: Frontend Developer | Crafts user experiences
- data: Database Expert | Optimizes data storage
- mobile: Mobile Specialist | Native app development

**QA Agents:**
- qa: Quality Engineer | Ensures reliability
- security: Security Expert | Protects against threats
- performance: Performance Analyst | Optimizes speed

**Operations:**
- devops: Platform Engineer | Manages infrastructure

User: "@agent-info backend"

Claude: **Backend Agent Details:**
- **Identity:** Pragmatic Problem Solver | Performance-Focused Engineer
- **Core Belief:** Efficient code is maintainable code
- **Strengths:** APIs, databases, scalability, microservices
- **Tech Preferences:** Go, Python, PostgreSQL, Redis
- **Compatible With:** frontend, data, qa, devops
- **Decision Framework:** performance > features, clarity > cleverness
- **Focus Areas:** API design, database optimization, caching strategies
```

### 2. Claude Suggests Agents

```
You: "I need to add payment processing"

Claude: For payment processing, I suggest using these agents:
- Backend Agent (payment API implementation)
- Security Agent (PCI compliance and security)
- QA Agent (payment flow testing)

[Approve these agents? (y)es / (n)o / (a)ll for session / (+)add more agents]

User: +frontend +devops

Claude: Added Frontend Agent and DevOps Agent. Proceeding with:
✓ Backend Agent
✓ Security Agent  
✓ QA Agent
✓ Frontend Agent
✓ DevOps Agent

[Using tool: ua_dev_backend_implement]
Backend Agent: Designing payment service with idempotency...

[Using tool: ua_qa_security_audit]
Security Agent: Implementing PCI compliance checks...
```

### 3. Manual Agent Invocation

```
User: "@riley help me understand what users really want from the search feature"

Claude: [Using tool: ua_design_requirements_analyze with Riley agent]
Riley here! Let me dig deeper into the search requirements...

Based on user feedback and behavior patterns:
- Users expect instant results (< 200ms)
- Typo tolerance is crucial (users make mistakes)
- Filter combinations are used by power users
- Most users only look at first 10 results

Hidden requirement discovered: Users want search history!

User: "@architect design this based on Riley's findings"

Claude: [Using tool: ua_architect_system_design]
Architect: Based on Riley's requirements, here's my design...
```

### 4. Session Preferences

```
User: "a" (during agent approval)

Claude: All agent suggestions will be auto-approved for this session. You can still:
- Use @agent for specific agents
- Say "no agents" to skip agent use
- Reset with "@reset-preferences"
```

## Configuration

### Claude Code Settings

```json
{
  "mcpServers": {
    "unified-agents": {
      "command": "ua-mcp-server",
      "args": ["--all-agents", "--interactive-mode"],
      "env": {
        "UA_AGENT_APPROVAL": "interactive",
        "UA_CONFIG_PATH": "~/.claude/agents.yml"
      }
    }
  }
}
```

### Agent Configuration (Shared)

```yaml
# ~/.claude/agents.yml
backend:
  personality: "pragmatic, performance-focused"
  preferences: ["PostgreSQL", "Redis", "Go"]
  compatible_with: ["frontend", "data", "qa", "devops"]
  
security:
  personality: "paranoid, thorough"
  preferences: ["OWASP", "zero-trust", "encryption"]
  compatible_with: ["backend", "qa", "devops"]
```

## Implementation Phases

### Phase 1: Core MCP Server
1. Create single MCP server with all agents
2. Implement basic tool exposure
3. Test with simple agent invocations

### Phase 2: Agent Discovery
1. Add agent listing tools
2. Add agent info/capabilities tools
3. Implement agent search functionality

### Phase 3: User Control
1. Add approval mechanism
2. Implement session preferences
3. Add @agent notation parsing

### Phase 4: Workflows
1. Port existing workflows to MCP
2. Add workflow status tracking
3. Enable custom workflow creation

### Phase 5: Advanced Features
1. Agent memory/context sharing
2. Multi-agent collaboration patterns
3. Learning from user preferences

## Usage Examples

### Example 1: Full Feature Development

```
You: "I need to build a real-time notification system"

Claude: This is a complex feature. I suggest using:
- Architect (system design)
- Backend (WebSocket implementation)
- Frontend (UI components)
- QA (real-time testing)
- DevOps (scaling strategy)

[Approve? y/n/a/+]
You: +security

Claude: Great choice! Adding Security Agent for secure channels.

[Using tool: ua_architect_system_design]
Architect: Designing pub/sub architecture with Redis...

[Using tool: ua_dev_backend_implement]
Backend: Implementing WebSocket server with auth...

[Using tool: ua_qa_security_audit]
Security: Adding encryption for notification channels...
```

### Example 2: Quick Agent Query

```
You: "@agents compatible-with frontend"

Claude: Agents compatible with Frontend:
- backend (API integration)
- ui (design collaboration)  
- mobile (shared components)
- qa (frontend testing)
- brand_maven (style consistency)
```

### Example 3: Workflow with Control

```
You: "Run the security audit workflow"

Claude: The security workflow will use:
- Security Agent (primary)
- QA Agent (security testing)
- Backend Agent (fix implementation)
- DevOps Agent (security monitoring)

[Approve? y/n/+]
You: y

[Using tool: ua_workflow_security]
Starting comprehensive security audit...
```

## Benefits

1. **Unified Interface**: All agents in one MCP server
2. **User Control**: Never surprised by agent behavior
3. **Flexibility**: Automatic or manual agent use
4. **Discovery**: Easy to explore agent capabilities
5. **Context Sharing**: Agents build on each other's work
6. **Workflow Support**: Complex multi-agent orchestration

## File Structure

```
~/.claude/
├── commands/              # Git slash commands (existing)
│   ├── commit.md
│   ├── branch.md
│   └── pr.md
├── agents.yml            # Agent configurations
├── mcp-servers/
│   └── unified-agents/   # MCP server config
└── preferences.yml       # User preferences
```

## Next Steps

1. Implement core MCP server structure
2. Add agent discovery tools
3. Implement user control mechanisms
4. Create agent invocation patterns
5. Test with real-world scenarios
6. Add workflow support
7. Document usage patterns

## Success Metrics

- Agent suggestions accepted >80% of time
- Manual agent invocation used regularly
- Session preferences reduce interruptions
- Workflow completion rate >90%
- User satisfaction with control level

## Future Enhancements

1. **Agent Learning**: Agents learn from user preferences
2. **Custom Agents**: Users can define their own agents
3. **Agent Marketplace**: Share agent configurations
4. **Visual Agent Builder**: GUI for agent creation
5. **Agent Analytics**: Track agent effectiveness