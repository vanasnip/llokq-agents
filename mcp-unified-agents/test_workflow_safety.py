#!/usr/bin/env python3
"""
Test script for Workflow Safety Features (approval, cancellation, dry-run)
"""
import json
import subprocess
import sys
import time
from pathlib import Path


def send_request(proc, request):
    """Send request to server and get response"""
    request_json = json.dumps(request) + '\n'
    proc.stdin.write(request_json.encode())
    proc.stdin.flush()
    
    response_line = proc.stdout.readline()
    return json.loads(response_line)


def test_workflow_safety_features():
    """Test workflow safety features"""
    server_path = Path(__file__).parent / "server.py"
    
    print("Starting MCP server workflow safety test...")
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
        
        # Test 2: Dry run a workflow
        print("\n2. Testing workflow dry run...")
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "ua_workflow_dry_run",
                "arguments": {
                    "template": "feature_development",
                    "inputs": {
                        "requirements": "User authentication system"
                    }
                }
            }
        })
        
        dry_run_data = json.loads(response['result']['content'][0]['text'])
        print(f"Dry run analysis for: {dry_run_data['template']}")
        print(f"Agents required: {', '.join(dry_run_data['agents_required'])}")
        print(f"Total steps: {dry_run_data['total_steps']}")
        print(f"Estimated time: {dry_run_data['resource_estimates']['estimated_time_seconds']}s")
        print(f"Estimated memory: {dry_run_data['resource_estimates']['estimated_memory_mb']}MB")
        
        # Test 3: Start workflow with approval required
        print("\n3. Testing workflow with approval required...")
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "ua_workflow_start",
                "arguments": {
                    "template": "bug_fix",
                    "inputs": {
                        "bug_description": "Login timeout error"
                    },
                    "require_approval": True
                }
            }
        })
        
        approval_data = json.loads(response['result']['content'][0]['text'])
        if approval_data.get('status') == 'pending_approval':
            print("✓ Workflow correctly requires approval")
            print(f"Agents needing approval: {', '.join(approval_data['agents_unapproved'])}")
            print(f"Message: {approval_data['message']}")
        else:
            print("✗ Workflow should have required approval!")
        
        # Test 4: Approve agents and retry
        print("\n4. Testing agent approval flow...")
        # First approve the needed agents
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "ua_approve_agents",
                "arguments": {
                    "action": "approve",
                    "agents": ["qa", "backend"]
                }
            }
        })
        
        approve_data = json.loads(response['result']['content'][0]['text'])
        print(f"Approved agents: {', '.join(approve_data['approved'])}")
        
        # Retry workflow start
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "ua_workflow_start",
                "arguments": {
                    "template": "bug_fix",
                    "inputs": {
                        "bug_description": "Login timeout error"
                    },
                    "require_approval": True
                }
            }
        })
        
        start_data = json.loads(response['result']['content'][0]['text'])
        if 'workflow_id' in start_data:
            workflow_id = start_data['workflow_id']
            print(f"✓ Workflow started after approval: {workflow_id}")
        else:
            print("✗ Workflow should have started after approval")
        
        # Test 5: Cancel a running workflow
        print("\n5. Testing workflow cancellation...")
        
        # Start another workflow
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "ua_workflow_start",
                "arguments": {
                    "template": "feature_development",
                    "inputs": {
                        "requirements": "Real-time notifications"
                    }
                }
            }
        })
        
        cancel_workflow_id = json.loads(response['result']['content'][0]['text'])['workflow_id']
        print(f"Started workflow to cancel: {cancel_workflow_id}")
        
        # Cancel it
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "ua_workflow_cancel",
                "arguments": {
                    "workflow_id": cancel_workflow_id,
                    "reason": "Testing cancellation feature"
                }
            }
        })
        
        cancel_data = json.loads(response['result']['content'][0]['text'])
        if cancel_data.get('status') == 'cancelled':
            print(f"✓ Workflow cancelled successfully")
            print(f"Reason: {cancel_data['reason']}")
        else:
            print("✗ Workflow cancellation failed")
        
        # Test 6: Resource limits
        print("\n6. Testing resource limits...")
        
        # Try to start many workflows to hit limit
        workflow_ids = []
        for i in range(6):  # Default limit is 5
            try:
                response = send_request(proc, {
                    "jsonrpc": "2.0",
                    "id": 10 + i,
                    "method": "tools/call",
                    "params": {
                        "name": "ua_workflow_start",
                        "arguments": {
                            "template": "api_design",
                            "inputs": {
                                "resource": f"Resource_{i}",
                                "operations": ["create", "read"]
                            }
                        }
                    }
                })
                
                result = response.get('result')
                if result and 'content' in result:
                    data = json.loads(result['content'][0]['text'])
                    if 'workflow_id' in data:
                        workflow_ids.append(data['workflow_id'])
                        print(f"Started workflow {i+1}: {data['workflow_id']}")
                elif 'error' in response:
                    print(f"✓ Resource limit enforced at workflow {i+1}")
                    print(f"Error: {response['error']['message']}")
                    break
                    
            except Exception as e:
                print(f"Error on workflow {i+1}: {e}")
        
        # Test 7: Set preferences for auto-approval
        print("\n7. Testing auto-approval preferences...")
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 20,
            "method": "tools/call",
            "params": {
                "name": "ua_set_preferences",
                "arguments": {
                    "auto_approve": True
                }
            }
        })
        
        pref_data = json.loads(response['result']['content'][0]['text'])
        print(f"Auto-approval enabled: {pref_data['preferences']['auto_approve']}")
        
        # Test workflow starts without approval
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 21,
            "method": "tools/call",
            "params": {
                "name": "ua_workflow_start",
                "arguments": {
                    "template": "bug_fix",
                    "inputs": {
                        "bug_description": "Auto-approved bug"
                    }
                }
            }
        })
        
        auto_data = json.loads(response['result']['content'][0]['text'])
        if 'workflow_id' in auto_data:
            print(f"✓ Workflow auto-started with auto-approval: {auto_data['workflow_id']}")
        
        print("\n✅ All workflow safety tests completed!")
        print("\nSafety features tested:")
        print("- Dry run analysis")
        print("- Approval requirements") 
        print("- Agent approval flow")
        print("- Workflow cancellation")
        print("- Resource limits")
        print("- Auto-approval preferences")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        stderr = proc.stderr.read().decode() if proc.stderr else ""
        if stderr:
            print(f"Server stderr: {stderr}")
    finally:
        # Clean up
        proc.terminate()
        proc.wait()


if __name__ == "__main__":
    test_workflow_safety_features()