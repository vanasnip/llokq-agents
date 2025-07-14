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
        for tool in response['result']['tools']:
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