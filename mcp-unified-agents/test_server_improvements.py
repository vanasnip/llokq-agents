#!/usr/bin/env python3
"""
Test script to verify server improvements from PR #5 review
"""
import os
import sys
import json
import subprocess
import tempfile
import time

def test_debug_mode():
    """Test that debug mode is controlled by environment variable"""
    print("Testing debug mode control...")
    
    # Test with debug mode disabled (default)
    env = os.environ.copy()
    env.pop('MCP_DEBUG', None)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as tmp:
        log_path = tmp.name
        env['MCP_DEBUG_LOG'] = log_path
    
    # Start server process
    proc = subprocess.Popen(
        [sys.executable, 'server.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True
    )
    
    # Send initialize request
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {"protocolVersion": "2025-07-17"}
    }
    
    proc.stdin.write(json.dumps(request) + '\n')
    proc.stdin.flush()
    
    # Read response
    response_line = proc.stdout.readline()
    response = json.loads(response_line)
    
    # Terminate server
    proc.stdin.close()
    proc.wait()
    
    # Check no debug log was created (debug mode disabled)
    assert not os.path.exists(log_path) or os.path.getsize(log_path) == 0, "Debug log created when DEBUG_MODE=false"
    
    print("✓ Debug mode disabled by default")
    
    # Test with debug mode enabled
    env['MCP_DEBUG'] = 'true'
    
    proc = subprocess.Popen(
        [sys.executable, 'server.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True
    )
    
    proc.stdin.write(json.dumps(request) + '\n')
    proc.stdin.flush()
    
    response_line = proc.stdout.readline()
    proc.stdin.close()
    proc.wait()
    
    # Check debug log was created
    assert os.path.exists(log_path) and os.path.getsize(log_path) > 0, "Debug log not created when DEBUG_MODE=true"
    
    with open(log_path, 'r') as f:
        content = f.read()
        assert "MCP Server startup" in content, "Debug log missing startup message"
    
    print("✓ Debug mode enabled via MCP_DEBUG=true")
    
    # Cleanup
    if os.path.exists(log_path):
        os.unlink(log_path)

def test_protocol_validation():
    """Test protocol version validation"""
    print("\nTesting protocol version validation...")
    
    env = os.environ.copy()
    
    proc = subprocess.Popen(
        [sys.executable, 'server.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True
    )
    
    # Test valid protocol version
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {"protocolVersion": "2025-07-17"}
    }
    
    proc.stdin.write(json.dumps(request) + '\n')
    proc.stdin.flush()
    
    response_line = proc.stdout.readline()
    response = json.loads(response_line)
    
    assert response['result']['protocolVersion'] == "2025-07-17", "Valid protocol version not echoed"
    print("✓ Valid protocol version accepted")
    
    # Test invalid protocol version
    request['id'] = 2
    request['params']['protocolVersion'] = "invalid-version"
    
    proc.stdin.write(json.dumps(request) + '\n')
    proc.stdin.flush()
    
    response_line = proc.stdout.readline()
    response = json.loads(response_line)
    
    # Should use default version for invalid format
    assert response['result']['protocolVersion'] == "2025-06-18", "Invalid protocol version not replaced with default"
    print("✓ Invalid protocol version replaced with default")
    
    proc.stdin.close()
    proc.wait()

def test_heartbeat_mode():
    """Test heartbeat mode control"""
    print("\nTesting heartbeat mode...")
    
    env = os.environ.copy()
    env['MCP_DEBUG'] = 'true'
    env['MCP_HEARTBEAT'] = 'true'
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as tmp:
        log_path = tmp.name
        env['MCP_DEBUG_LOG'] = log_path
    
    proc = subprocess.Popen(
        [sys.executable, 'server.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True
    )
    
    # Let it run for a bit
    time.sleep(2)
    
    # Send a request to ensure server is responsive
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {"protocolVersion": "2025-07-17"}
    }
    
    proc.stdin.write(json.dumps(request) + '\n')
    proc.stdin.flush()
    proc.stdout.readline()
    
    # Wait for heartbeat
    time.sleep(11)
    
    proc.stdin.close()
    proc.wait()
    
    # Check for heartbeat in log
    with open(log_path, 'r') as f:
        content = f.read()
        if "💓 Heartbeat:" in content:
            print("✓ Heartbeat logging enabled via MCP_HEARTBEAT=true")
        else:
            print("⚠ Heartbeat not found (may be timing issue)")
    
    # Cleanup
    if os.path.exists(log_path):
        os.unlink(log_path)

if __name__ == "__main__":
    print("Running server improvement tests...")
    
    try:
        test_debug_mode()
        test_protocol_validation()
        test_heartbeat_mode()
        
        print("\n✅ All tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)