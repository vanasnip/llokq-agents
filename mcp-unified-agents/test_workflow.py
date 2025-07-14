#!/usr/bin/env python3
"""
Test script for Workflow functionality in MCP Server
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


def test_workflow_features():
    """Test the workflow functionality"""
    server_path = Path(__file__).parent / "server.py"
    
    print("Starting MCP server workflow test...")
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
        print(f"Server initialized: {response['result']['serverInfo']}")
        
        # Test 2: List tools (should include workflow tools)
        print("\n2. Checking workflow tools...")
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        })
        
        workflow_tools = [
            tool for tool in response['result']['tools'] 
            if tool['name'].startswith('ua_workflow_')
        ]
        
        print(f"Found {len(workflow_tools)} workflow tools:")
        for tool in workflow_tools:
            print(f"  - {tool['name']}: {tool['description']}")
        
        # Test 3: List workflow templates
        print("\n3. Testing workflow templates...")
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "ua_workflow_templates",
                "arguments": {}
            }
        })
        
        templates_data = json.loads(response['result']['content'][0]['text'])
        print(f"Available templates: {templates_data['total']}")
        for template in templates_data['templates']:
            print(f"  - {template['id']}: {template['name']} ({template['steps_count']} steps)")
        
        # Test 4: Suggest workflow for a task
        print("\n4. Testing workflow suggestions...")
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "ua_workflow_suggest",
                "arguments": {
                    "task": "I need to build a REST API for user management"
                }
            }
        })
        
        suggestions_data = json.loads(response['result']['content'][0]['text'])
        print(f"Task: {suggestions_data['task']}")
        print("Workflow suggestions:")
        for suggestion in suggestions_data['suggestions']:
            print(f"  - {suggestion['template']} (confidence: {suggestion['confidence']})")
            print(f"    Reason: {suggestion['reason']}")
        
        # Test 5: Start a workflow
        print("\n5. Testing workflow execution...")
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "ua_workflow_start",
                "arguments": {
                    "template": "feature_development",
                    "inputs": {
                        "requirements": "User authentication system with JWT tokens",
                        "constraints": ["Must support refresh tokens", "PostgreSQL database"]
                    }
                }
            }
        })
        
        start_data = json.loads(response['result']['content'][0]['text'])
        workflow_id = start_data['workflow_id']
        print(f"Started workflow: {workflow_id}")
        print(f"Template: {start_data['template']}")
        
        # Test 6: Check workflow status
        print("\n6. Checking workflow status...")
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "ua_workflow_status",
                "arguments": {
                    "workflow_id": workflow_id
                }
            }
        })
        
        status_data = json.loads(response['result']['content'][0]['text'])
        workflow = status_data['workflow']
        print(f"Workflow status: {workflow['status']}")
        print(f"Current step: {workflow['current_step']}")
        print(f"Steps completed: {len(workflow['steps_completed'])}")
        
        if workflow['steps_completed']:
            print("\nCompleted steps:")
            for step in workflow['steps_completed']:
                print(f"  - Step {step['step']}: {step['agent']}.{step['tool']}")
        
        # Test 7: List all workflows
        print("\n7. Listing all workflows...")
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "ua_workflow_list",
                "arguments": {}
            }
        })
        
        list_data = json.loads(response['result']['content'][0]['text'])
        print(f"Total workflows: {list_data['total']}")
        for wf in list_data['workflows']:
            print(f"  - {wf['id']}: {wf['template']} ({wf['status']})")
        
        # Test 8: Start another workflow (bug fix)
        print("\n8. Testing bug fix workflow...")
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "tools/call",
            "params": {
                "name": "ua_workflow_start",
                "arguments": {
                    "template": "bug_fix",
                    "inputs": {
                        "bug_description": "Login fails with 500 error",
                        "stack_trace": "TypeError: Cannot read property 'id' of undefined"
                    }
                }
            }
        })
        
        bug_data = json.loads(response['result']['content'][0]['text'])
        print(f"Started bug fix workflow: {bug_data['workflow_id']}")
        
        print("\n✅ All workflow tests passed!")
        
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
    test_workflow_features()