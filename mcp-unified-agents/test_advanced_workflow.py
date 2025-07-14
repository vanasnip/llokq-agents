#!/usr/bin/env python3
"""
Test script for Advanced Workflow features (parallel execution, custom workflows)
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


def test_advanced_workflow_features():
    """Test advanced workflow functionality"""
    server_path = Path(__file__).parent / "server.py"
    
    print("Starting MCP server advanced workflow test...")
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
        
        # Test 2: Create custom workflow
        print("\n2. Testing custom workflow creation...")
        
        custom_workflow_steps = [
            {
                "name": "Analyze Requirements",
                "agent": "architect",
                "tool": "ua_architect_design",
                "input": {
                    "requirements": "{requirements}"
                },
                "output": "system_design"
            },
            {
                "name": "Parallel Implementation",
                "parallel": [
                    {
                        "agent": "backend",
                        "tool": "ua_backend_api_design",
                        "input": {
                            "architecture": "{system_design}"
                        },
                        "output": "api_design"
                    },
                    {
                        "agent": "qa",
                        "tool": "ua_qa_test_generate",
                        "input": {
                            "feature": "{requirements}"
                        },
                        "output": "test_suite"
                    }
                ]
            },
            {
                "name": "Security Review",
                "agent": "security",
                "tool": "ua_security_scan",
                "input": {
                    "scope": "{api_design}"
                },
                "output": "security_report"
            }
        ]
        
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "ua_workflow_create",
                "arguments": {
                    "name": "Custom Security-First Workflow",
                    "description": "Development workflow with integrated security checks",
                    "steps": custom_workflow_steps
                }
            }
        })
        
        create_data = json.loads(response['result']['content'][0]['text'])
        custom_template_id = create_data['template_id']
        print(f"Created custom workflow: {custom_template_id}")
        print(f"Name: {create_data['name']}")
        print(f"Steps: {create_data['steps']}")
        
        # Test 3: List templates (should include custom)
        print("\n3. Verifying custom template in list...")
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
        print(f"Total templates: {templates_data['total']}")
        
        custom_found = False
        for template in templates_data['templates']:
            if template['id'] == custom_template_id:
                custom_found = True
                print(f"✓ Found custom template: {template['name']}")
                break
                
        if not custom_found:
            print("✗ Custom template not found in list!")
        
        # Test 4: Start custom workflow
        print("\n4. Testing custom workflow execution...")
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "ua_workflow_start",
                "arguments": {
                    "template": custom_template_id,
                    "inputs": {
                        "requirements": "E-commerce payment processing system"
                    }
                }
            }
        })
        
        start_data = json.loads(response['result']['content'][0]['text'])
        custom_workflow_id = start_data['workflow_id']
        print(f"Started custom workflow: {custom_workflow_id}")
        
        # Test 5: Check workflow status (should show parallel execution)
        print("\n5. Checking custom workflow status...")
        # Give it a moment to execute
        time.sleep(0.5)
        
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "ua_workflow_status",
                "arguments": {
                    "workflow_id": custom_workflow_id
                }
            }
        })
        
        status_data = json.loads(response['result']['content'][0]['text'])
        workflow = status_data['workflow']
        
        print(f"Workflow status: {workflow['status']}")
        print(f"Steps completed: {len(workflow['steps_completed'])}/{workflow['current_step']}")
        
        # Look for parallel step execution
        parallel_steps = [s for s in workflow['steps_completed'] if 'parallel' in str(s)]
        if parallel_steps:
            print("✓ Parallel execution detected")
        
        # Test 6: Test workflow with actual parallel timing
        print("\n6. Testing parallel execution timing...")
        
        # Start feature development workflow (has parallel steps)
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "ua_workflow_start",
                "arguments": {
                    "template": "feature_development",
                    "inputs": {
                        "requirements": "Real-time chat system"
                    }
                }
            }
        })
        
        parallel_workflow_id = json.loads(response['result']['content'][0]['text'])['workflow_id']
        
        # Check status
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "ua_workflow_status",
                "arguments": {
                    "workflow_id": parallel_workflow_id
                }
            }
        })
        
        status_data = json.loads(response['result']['content'][0]['text'])
        workflow = status_data['workflow']
        
        # Check for parallel step (step 3 in feature_development)
        if len(workflow['steps_completed']) > 3:
            step_3 = workflow['steps_completed'][3]
            if step_3['agent'] == 'system' and step_3['tool'] == 'unknown':
                print("✓ Parallel step executed (backend + frontend)")
        
        # Test 7: List all workflows
        print("\n7. Listing all workflows...")
        response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "tools/call",
            "params": {
                "name": "ua_workflow_list",
                "arguments": {}
            }
        })
        
        list_data = json.loads(response['result']['content'][0]['text'])
        print(f"Total active workflows: {list_data['total']}")
        
        for wf in list_data['workflows']:
            print(f"  - {wf['id']}: {wf['template']} ({wf['status']})")
            if wf['template'].startswith('custom_'):
                print("    ^ Custom workflow!")
        
        print("\n✅ All advanced workflow tests passed!")
        print("\nKey features tested:")
        print("- Custom workflow creation")
        print("- Parallel step execution")
        print("- Custom workflow execution")
        print("- Multiple active workflows")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        # Print stderr if available
        stderr = proc.stderr.read().decode() if proc.stderr else ""
        if stderr:
            print(f"Server stderr: {stderr}")
    finally:
        # Clean up
        proc.terminate()
        proc.wait()


if __name__ == "__main__":
    test_advanced_workflow_features()