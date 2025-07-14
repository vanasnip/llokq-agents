#!/usr/bin/env python3
"""
Test script for Unified Agents MCP Server
Tests basic functionality without requiring Claude Code
"""
import json
import subprocess
import sys
from pathlib import Path


def send_request(proc, request):
    """Send request to server and get response"""
    request_json = json.dumps(request) + '\n'
    proc.stdin.write(request_json.encode())
    proc.stdin.flush()
    
    response_line = proc.stdout.readline()
    return json.loads(response_line)


def test_mcp_server():
    """Test the MCP server functionality"""
    server_path = Path(__file__).parent / "server.py"
    
    print("Starting MCP server test...")
    print(f"Server path: {server_path}")
    
    # Start the server
    proc = subprocess.Popen(
        [sys.executable, str(server_path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False
    )
    
    try:
        # Test 1: Initialize
        print("\n1. Testing initialize...")
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        })
        print(f"Response: {json.dumps(response, indent=2)}")
        
        # Test 2: List tools
        print("\n2. Testing tools/list...")
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        })
        print(f"Available tools: {len(response['result']['tools'])}")
        discovery_tools = []
        agent_tools = []
        for tool in response['result']['tools']:
            if tool['name'].startswith('ua_agent') or tool['name'].startswith('ua_capability'):
                discovery_tools.append(tool)
            else:
                agent_tools.append(tool)
        
        print("\nDiscovery tools:")
        for tool in discovery_tools:
            print(f"  - {tool['name']}: {tool['description']}")
        
        print("\nAgent-specific tools:")
        for tool in agent_tools:
            print(f"  - {tool['name']}: {tool['description']}")
        
        # Test 3: Call QA test generation tool
        print("\n3. Testing QA test generation...")
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "ua_qa_test_generate",
                "arguments": {
                    "feature": "User Login",
                    "test_type": "unit"
                }
            }
        })
        print("QA Agent response:")
        print(response['result']['content'][0]['text'][:500] + "...")
        
        # Test 4: Call Backend API design tool
        print("\n4. Testing Backend API design...")
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "ua_backend_api_design",
                "arguments": {
                    "resource": "User",
                    "operations": ["create", "read", "update", "list"]
                }
            }
        })
        print("Backend Agent response:")
        print(response['result']['content'][0]['text'][:500] + "...")
        
        # Test 5: Call Architect design tool
        print("\n5. Testing Architect system design...")
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "ua_architect_design",
                "arguments": {
                    "requirements": "Real-time chat system with 10k concurrent users",
                    "constraints": ["Low latency (<100ms)", "Horizontal scalability"]
                }
            }
        })
        print("Architect response:")
        print(response['result']['content'][0]['text'][:500] + "...")
        
        # Test 6: Test discovery tools
        print("\n6. Testing agent discovery tools...")
        
        # Test ua_agents_list
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "ua_agents_list",
                "arguments": {}
            }
        })
        print("Agent list response (first 300 chars):")
        print(response['result']['content'][0]['text'][:300] + "...")
        
        # Test ua_agent_info
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "ua_agent_info",
                "arguments": {
                    "agent_id": "backend"
                }
            }
        })
        print("\nBackend agent info (first 400 chars):")
        print(response['result']['content'][0]['text'][:400] + "...")
        
        # Test ua_capability_search
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "tools/call",
            "params": {
                "name": "ua_capability_search",
                "arguments": {
                    "query": "api"
                }
            }
        })
        print("\nSearch for 'api' capabilities:")
        print(response['result']['content'][0]['text'])
        
        # Test ua_agent_compatible
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 9,
            "method": "tools/call",
            "params": {
                "name": "ua_agent_compatible",
                "arguments": {
                    "agent_id": "backend"
                }
            }
        })
        print("\nAgents compatible with backend:")
        print(response['result']['content'][0]['text'])
        
        # Test 7: Test control tools
        print("\n7. Testing user control tools...")
        
        # Test ua_suggest_agents
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 10,
            "method": "tools/call",
            "params": {
                "name": "ua_suggest_agents",
                "arguments": {
                    "task": "I need to build a REST API for user management with testing"
                }
            }
        })
        print("\nAgent suggestions for REST API task:")
        suggestion_data = json.loads(response['result']['content'][0]['text'])
        print(json.dumps(suggestion_data, indent=2))
        suggestion_id = suggestion_data['suggestion_id']
        
        # Test ua_approve_agents
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 11,
            "method": "tools/call",
            "params": {
                "name": "ua_approve_agents",
                "arguments": {
                    "action": "approve",
                    "agents": ["backend", "qa"],
                    "suggestion_id": suggestion_id
                }
            }
        })
        print("\nApproval result:")
        print(json.dumps(json.loads(response['result']['content'][0]['text']), indent=2))
        
        # Test ua_set_preferences
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 12,
            "method": "tools/call",
            "params": {
                "name": "ua_set_preferences",
                "arguments": {
                    "auto_approve": True,
                    "block_agents": ["architect"]
                }
            }
        })
        print("\nPreferences updated:")
        print(json.dumps(json.loads(response['result']['content'][0]['text']), indent=2))
        
        # Test new suggestion with auto-approval
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 13,
            "method": "tools/call",
            "params": {
                "name": "ua_suggest_agents",
                "arguments": {
                    "task": "Design a scalable system architecture"
                }
            }
        })
        print("\nNew suggestion with auto-approval enabled:")
        print(json.dumps(json.loads(response['result']['content'][0]['text']), indent=2))
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        # Print stderr if available
        stderr = proc.stderr.read().decode() if proc.stderr else ""
        if stderr:
            print(f"Server stderr: {stderr}")
    finally:
        # Clean up
        proc.terminate()
        proc.wait()


if __name__ == "__main__":
    test_mcp_server()