#!/usr/bin/env python3
"""
Debug test to see actual response formats
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

def debug_test():
    print("Debug test to check response formats...")
    
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
    
    # Test ua_agents_list
    print("\n1. ua_agents_list response:")
    response = send_request(proc, {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "ua_agents_list",
            "arguments": {}
        }
    })
    print(f"   Type: {type(response.get('result'))}")
    print(f"   Content: {json.dumps(response.get('result'), indent=2)[:200]}...")
    
    proc.stdin.close()
    proc.wait()

if __name__ == "__main__":
    debug_test()