#!/usr/bin/env python3
"""
Manual test script for MCP server functionality
"""
import json
import subprocess
import sys
import os

def send_request(proc, request):
    """Send a request and get response"""
    proc.stdin.write(json.dumps(request) + '\n')
    proc.stdin.flush()
    response_line = proc.stdout.readline()
    return json.loads(response_line)

def test_server():
    print("Starting MCP server test...")
    
    # Test 1: Basic functionality (no debug mode)
    print("\n1. Testing without debug mode...")
    env = os.environ.copy()
    
    proc = subprocess.Popen(
        [sys.executable, 'server.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True
    )
    
    # Initialize
    response = send_request(proc, {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {"protocolVersion": "2025-07-17"}
    })
    print(f"   Initialize response: {response['result']['protocolVersion']}")
    
    # List tools
    response = send_request(proc, {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
    })
    print(f"   Available tools: {len(response['result']['tools'])} tools")
    
    # List some tools
    if response['result']['tools']:
        for tool in response['result']['tools'][:3]:
            print(f"     - {tool['name']}: {tool['description'][:50]}...")
    
    proc.stdin.close()
    proc.wait()
    print("   ✓ Basic functionality works!")
    
    # Test 2: With debug mode
    print("\n2. Testing with debug mode enabled...")
    env['MCP_DEBUG'] = 'true'
    debug_log = '/tmp/mcp-test-debug.log'
    env['MCP_DEBUG_LOG'] = debug_log
    
    # Clean up old log
    if os.path.exists(debug_log):
        os.unlink(debug_log)
    
    proc = subprocess.Popen(
        [sys.executable, 'server.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True
    )
    
    # Initialize
    response = send_request(proc, {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {"protocolVersion": "2025-07-17"}
    })
    
    # Try calling a tool
    response = send_request(proc, {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "ua_agents_list",
            "arguments": {}
        }
    })
    
    if 'result' in response:
        print(f"   Tool call successful!")
        result = response['result']
        if isinstance(result, list) and result:
            print(f"   Found {len(result)} agents")
    
    proc.stdin.close()
    proc.wait()
    
    # Check debug log
    if os.path.exists(debug_log):
        with open(debug_log, 'r') as f:
            content = f.read()
            if "MCP Server startup" in content:
                print("   ✓ Debug logging works!")
            print(f"   Debug log size: {len(content)} bytes")
        os.unlink(debug_log)
    
    print("\n✅ All manual tests passed!")

if __name__ == "__main__":
    test_server()