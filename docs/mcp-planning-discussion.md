# MCP Server Planning Discussion

## Discussion Summary

This document captures the planning discussion for transitioning the Unified Agents system to work as an MCP server for Claude Code integration.

## Key Decisions

### 1. Single MCP Server Approach
**Decision**: Create one unified MCP server containing all agents rather than separate servers per agent type.
**Rationale**: 
- Simpler configuration
- Shared context between agents
- Easier agent collaboration

### 2. Hybrid CLI + MCP Model
**Decision**: Keep CLI for quick tasks (like `/commit`) while adding MCP for complex agent interactions.
**Rationale**:
- CLI is faster for simple operations
- MCP better for conversational, exploratory work
- Different tools for different jobs

### 3. User Control Over Agents
**Decision**: Users must approve agent selection with options for:
- Individual approval
- Session-wide approval
- Adding additional agents
- Manual agent invocation via @notation

**Rationale**: 
- User maintains control
- No surprise agent activations
- Flexibility in agent selection

### 4. Agent Discovery Features
**Decision**: Add comprehensive agent discovery tools:
- List all agents
- Get detailed agent info
- Find compatible agents
- Search by capability

**Rationale**:
- Users need to understand what agents do
- Helps with manual agent selection
- Enables informed decisions

## Architecture Overview

The MCP server will expose tools in these categories:
- **Agent Discovery**: Tools for exploring available agents
- **Design Tools**: 5 design agents
- **Architecture Tools**: 2 architecture agents  
- **Development Tools**: 4 development agents
- **QA Tools**: 3 QA/testing agents
- **Operations Tools**: 1 DevOps agent
- **Workflow Tools**: Multi-agent workflows
- **Meta Tools**: User control and preferences

## Key Insights

1. **Not a Claude Code Extension**: This system is primarily a standalone tool that happens to have MCP integration capabilities.

2. **User Control is Critical**: Users want to maintain control over which agents are used and when.

3. **Agent Discovery**: Users need ways to explore and understand agent capabilities before using them.

4. **Workflow Integration**: Multi-agent workflows are a key value proposition.

## Next Steps

1. Implement the MCP server based on the saved plan
2. Create agent discovery tools first
3. Add user control mechanisms
4. Test with real scenarios
5. Iterate based on usage patterns

## References

- [MCP Server Plan](../MCP_SERVER_PLAN.md)
- [Unified Agents Documentation](../README.md)
- [Agent Catalog](agents.md)