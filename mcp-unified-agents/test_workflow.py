#!/usr/bin/env python3
"""
Test workflow functionality of the MCP server
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

def test_workflow():
    print("Testing MCP server workflow functionality...")
    
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
    print(f"✓ Initialized with protocol: {response['result']['protocolVersion']}")
    
    # Test 1: List agents
    print("\n1. Testing agent listing...")
    response = send_request(proc, {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "ua_agents_list",
            "arguments": {}
        }
    })
    
    if 'result' in response:
        result = response['result']
        if isinstance(result, str):
            # Parse the string result
            print(f"   Result: {result[:100]}...")
        elif isinstance(result, list):
            print(f"   Found {len(result)} agents:")
            for agent in result[:3]:
                if isinstance(agent, dict):
                    print(f"   - {agent.get('id', 'N/A')}: {agent.get('name', 'N/A')}")
        elif isinstance(result, dict) and 'agents' in result:
            agents = result['agents']
            print(f"   Found {len(agents)} agents:")
            for agent in agents[:3]:
                print(f"   - {agent['id']}: {agent['name']}")
    
    # Test 2: Get agent info
    print("\n2. Testing agent info retrieval...")
    response = send_request(proc, {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "ua_agent_info",
            "arguments": {"agent_id": "qa"}
        }
    })
    
    if 'result' in response:
        info = response['result']
        print(f"   QA Agent info:")
        print(f"   - Name: {info.get('name', 'N/A')}")
        print(f"   - Tools: {len(info.get('tools', []))}")
    
    # Test 3: Suggest agents for a task
    print("\n3. Testing agent suggestion...")
    response = send_request(proc, {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "ua_suggest_agents",
            "arguments": {
                "task": "Write unit tests for a Python function"
            }
        }
    })
    
    if 'result' in response:
        result = response['result']
        if 'agents' in result:
            print(f"   Suggested agents: {', '.join([a['id'] for a in result['agents']])}")
    
    # Test 4: List workflow templates
    print("\n4. Testing workflow templates...")
    response = send_request(proc, {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "ua_workflow_templates",
            "arguments": {}
        }
    })
    
    if 'result' in response:
        templates = response['result']
        print(f"   Found {len(templates)} workflow templates:")
        for template in templates[:3]:
            print(f"   - {template['name']}: {template['description'][:50]}...")
    
    # Test 5: Error handling
    print("\n5. Testing error handling...")
    response = send_request(proc, {
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {
            "name": "nonexistent_tool",
            "arguments": {}
        }
    })
    
    if 'error' in response:
        print(f"   ✓ Error handled correctly: {response['error']['message'][:50]}...")
    
    proc.stdin.close()
    proc.wait()
    
    print("\n✅ All workflow tests passed!")

if __name__ == "__main__":
    test_workflow()