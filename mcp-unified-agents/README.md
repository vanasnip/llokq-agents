# Unified Agents MCP Server

A lean Model Context Protocol (MCP) server that exposes AI development agents as tools for Claude Code.

## Quick Start

1. **No dependencies required** - Uses only Python standard library

2. **Configure Claude Code** (`~/.claude/claude_code_config.json`):

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

3. **Start Claude Code** - The MCP server will start automatically

4. **Use agent tools** in your conversations:
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
├── server.py       # MCP server implementation
├── agents.json     # Agent definitions and capability graph
├── test_server.py  # Test script for verification
└── README.md       # This file
```

## How It Works

1. **Agent Definitions**: Agents are defined in `agents.json` as data, not code
2. **Capability Graph**: Shows relationships between agent capabilities
3. **Tool Exposure**: Each agent's tools are exposed via MCP protocol
4. **Simple Transport**: Uses stdio for communication with Claude Code
5. **Serial Processing**: Processes requests one at a time for simplicity

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

## Testing the Server

You can test the server without Claude Code using the included test script:

```bash
python test_server.py
```

To manually test with JSON-RPC:

```bash
# List available tools
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python server.py | jq

# Call a specific tool
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"ua_qa_test_generate","arguments":{"feature":"Login","test_type":"unit"}}}' | python server.py | jq
```

## Troubleshooting

### Server not starting
- **Check Claude Code config path**: Ensure the path to server.py is absolute
- **Python version**: Requires Python 3.6+ (uses f-strings)
- **File permissions**: Ensure server.py is executable

### Tools not appearing
- **Restart Claude Code**: Changes to MCP config require restart
- **Check logs**: Run `python server.py` directly to see error messages
- **Validate manifest**: Ensure agents.json is valid JSON

### Errors in responses
- **Invalid JSON**: Server returns error code -32700 for parse errors
- **Unknown method**: Returns -32601 for unrecognized methods
- **Missing parameters**: Returns -32602 with details about missing params
- **Check server logs**: Errors are logged with timestamps

### Common Issues

| Issue | Solution |
|-------|----------|
| "Manifest file not found" | Ensure agents.json is in same directory as server.py |
| "Invalid manifest structure" | Check agents.json matches expected schema |
| "Unknown tool" | Tool names must start with `ua_` prefix |
| No output from server | Server uses stdio - must be run with proper JSON-RPC input |

## Development

To modify or extend:
1. Edit `agents.json` to add/modify agents
2. Update tool handlers in `server.py`
3. Run `test_server.py` to verify changes
4. Test with Claude Code

### Adding a New Agent

1. Add agent definition to `agents.json`:
```json
"new_agent": {
  "name": "New Agent",
  "description": "Agent description",
  "tools": [
    {
      "name": "ua_new_agent_tool",
      "description": "Tool description",
      "parameters": {
        "param1": {"type": "string"}
      }
    }
  ]
}
```

2. Add handler method in `server.py`:
```python
def _handle_new_agent_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    # Implementation
```

3. Update routing in `_handle_call_tool`

---

Part of the Unified Agents project - bringing AI agent collaboration to your development workflow.