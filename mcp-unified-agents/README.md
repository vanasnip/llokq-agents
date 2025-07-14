# Unified Agents MCP Server

A lean Model Context Protocol (MCP) server that exposes AI development agents as tools for Claude Code.

## Quick Start

1. **Configure Claude Code** (`~/.claude/claude_code_config.json`):

```json
{
  "mcpServers": {
    "unified-agents": {
      "command": "python",
      "args": ["/path/to/mcp-unified-agents/server.py"],
      "env": {}
    }
  }
}
```

2. **Start Claude Code** - The MCP server will start automatically

3. **Use agent tools** in your conversations:
   - Generate tests: "Use the QA agent to generate unit tests for the login feature"
   - Design APIs: "Have the backend agent design a REST API for user management"
   - System architecture: "Ask the architect to design a scalable notification system"

## Available Agents (MVP)

### QA Agent
Quality assurance and testing specialist
- `ua_qa_test_generate` - Generate test cases (unit, integration, e2e)
- `ua_qa_analyze_bug` - Analyze bugs and suggest fixes

### Backend Agent
Backend development and API specialist
- `ua_backend_api_design` - Design REST APIs
- `ua_backend_optimize` - Suggest code optimizations

### System Architect
System design and architecture expert
- `ua_architect_design` - Design system architecture

## Architecture

```
mcp-unified-agents/
├── server.py       # MCP server implementation (~400 lines)
├── agents.yaml     # Agent definitions and capability graph
└── README.md       # This file
```

## How It Works

1. **Agent Definitions**: Agents are defined in `agents.yaml` as data, not code
2. **Capability Graph**: Shows relationships between agent capabilities
3. **Tool Exposure**: Each agent's tools are exposed via MCP protocol
4. **Simple Transport**: Uses stdio for communication with Claude Code

## Example Usage

```
You: I need to add user authentication to my app

Claude: I'll help you design the authentication system. Let me use our agents to create a comprehensive solution.

[Using tool: ua_architect_design]
System Architect: Designing authentication architecture...

[Using tool: ua_backend_api_design]
Backend Agent: Creating REST API for authentication...

[Using tool: ua_qa_test_generate]
QA Agent: Generating test cases for authentication flow...
```

## Capability Graph

The system uses a capability graph to understand relationships:
- **Requires**: What capabilities are prerequisites
- **Provides**: What capabilities this enables
- **Complements**: What works well together

## Future Expansion

This MVP is designed to expand to:
- 15+ specialized agents
- Agent discovery tools
- User control mechanisms
- Multi-agent workflows
- Custom agent definitions

## Troubleshooting

1. **Server not starting**: Check Claude Code config path
2. **Tools not appearing**: Restart Claude Code
3. **Errors in responses**: Check server.py logs

## Development

To modify or extend:
1. Edit `agents.yaml` to add/modify agents
2. Update tool handlers in `server.py`
3. Test with Claude Code

---

Part of the Unified Agents project - bringing AI agent collaboration to your development workflow.