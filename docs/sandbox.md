# Sandboxed Execution Framework

## Overview

The sandboxed execution framework provides secure, isolated environments for running potentially untrusted code or commands. It supports both process-based and Docker-based sandboxing with configurable resource limits and security policies.

## Architecture

### Core Components

1. **SandboxEnvironment** - Abstract base class for sandbox implementations
2. **ProcessSandbox** - Process-based isolation using resource limits
3. **DockerSandbox** - Container-based isolation for stronger security
4. **SandboxManager** - Manages sandbox lifecycle and cleanup
5. **Sandboxed Tools** - Pre-built tools for common sandboxed operations

### Security Features

- **Resource Limits**
  - Memory usage caps
  - CPU time limits
  - File size restrictions
  - Process count limits
  - Open file descriptors limits

- **Network Isolation**
  - Network access can be disabled
  - Whitelist of allowed hosts
  - No network access by default

- **Filesystem Protection**
  - Temporary isolated directories
  - Read-only root filesystem (Docker)
  - Path traversal prevention

- **Command Validation**
  - Whitelist of allowed commands
  - Dangerous pattern detection
  - Shell metacharacter filtering

## Usage

### Basic Sandbox Execution

```python
from unified.sandbox import SandboxConfig, ProcessSandbox

# Configure sandbox
config = SandboxConfig(
    max_memory_mb=256,
    max_cpu_seconds=10,
    timeout_seconds=30,
    allow_network=False
)

# Create and setup sandbox
sandbox = ProcessSandbox(config)
sandbox.setup()

# Execute command
result = sandbox.execute("echo 'Hello, Sandbox!'")
if result.success:
    print(result.output['stdout'])
else:
    print(f"Error: {result.error}")

# Always cleanup
sandbox.cleanup()
```

### Using Sandbox Manager

```python
from unified.sandbox import get_sandbox_manager, SandboxConfig

manager = get_sandbox_manager()

# Create sandbox
config = SandboxConfig(timeout_seconds=5)
sandbox = manager.create_sandbox("my_sandbox", config)

# Execute commands
result = sandbox.execute(["python3", "-c", "print(2+2)"])

# Cleanup
manager.cleanup_sandbox("my_sandbox")
```

### Sandboxed Tools

#### Command Execution

```python
from unified.tools import ToolContext
from unified.tools.sandboxed_tools import SandboxedCommandTool

tool = SandboxedCommandTool()
context = ToolContext(working_directory=Path.cwd())

result = tool.execute(context, "ls -la")
```

#### Python Code Execution

```python
from unified.tools.sandboxed_tools import SandboxedPythonTool

tool = SandboxedPythonTool()
result = tool.execute(context, """
result = sum(range(100))
""")
print(result.output)  # 4950
```

#### File Operations

```python
from unified.tools.sandboxed_tools import SandboxedFileTool

tool = SandboxedFileTool()

# Write file
result = tool.execute(context, "write", "test.txt", "Hello, World!")

# Read file
result = tool.execute(context, "read", "test.txt")
print(result.output)  # Hello, World!
```

#### Network Requests

```python
from unified.tools.sandboxed_tools import SandboxedNetworkTool

tool = SandboxedNetworkTool(allowed_hosts=["api.example.com"])
result = tool.execute(context, "https://api.example.com/data", "GET")
```

## Configuration

### SandboxConfig Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| max_memory_mb | int | 512 | Maximum memory usage in MB |
| max_cpu_seconds | int | 30 | Maximum CPU time in seconds |
| max_file_size_mb | int | 100 | Maximum file size in MB |
| max_process_count | int | 10 | Maximum number of processes |
| max_open_files | int | 100 | Maximum open file descriptors |
| allow_network | bool | False | Allow network access |
| allowed_hosts | List[str] | [] | Whitelist of allowed hosts |
| timeout_seconds | int | 60 | Execution timeout |
| allowed_commands | List[str] | [] | Whitelist of allowed commands |

### Docker vs Process Sandbox

**ProcessSandbox**
- Lightweight, fast startup
- Uses OS-level resource limits
- Good for trusted environments
- Platform-dependent features

**DockerSandbox**
- Stronger isolation
- Consistent across platforms
- Better security boundaries
- Requires Docker installation

## Security Considerations

1. **Defense in Depth**: The sandbox provides one layer of security but should not be the only protection mechanism.

2. **Resource Exhaustion**: Configure appropriate limits to prevent denial of service.

3. **Escape Risks**: No sandbox is perfect. Monitor for unusual behavior and keep systems updated.

4. **Input Validation**: Always validate and sanitize input before sandbox execution.

5. **Least Privilege**: Run sandboxes with minimal required permissions.

## Best Practices

1. **Always Cleanup**: Use try/finally or context managers to ensure cleanup.

2. **Set Appropriate Limits**: Balance security with functionality needs.

3. **Monitor Resource Usage**: Check resource usage in results for optimization.

4. **Use Specific Tools**: Prefer sandboxed tools over raw sandbox execution.

5. **Test Timeouts**: Ensure timeouts are appropriate for expected workloads.

## Error Handling

```python
from unified.sandbox import SandboxStatus

result = sandbox.execute(command)

if result.status == SandboxStatus.TIMEOUT:
    # Handle timeout
    logger.warning(f"Command timed out after {result.duration}s")
elif result.status == SandboxStatus.FAILED:
    # Handle failure
    logger.error(f"Command failed: {result.error}")
elif result.status == SandboxStatus.COMPLETED:
    # Process successful result
    process_output(result.output)
```

## Integration with Tool Framework

Tools can automatically use sandboxing when the context specifies it:

```python
context = ToolContext(
    working_directory=Path.cwd(),
    sandbox=True  # Enable sandboxing
)

# Any tool execution will now use sandbox if supported
result = command_tool.execute(context, "potentially_dangerous_command")
```

## Examples

### Running Untrusted Scripts

```python
# Configure strict sandbox for untrusted code
config = SandboxConfig(
    max_memory_mb=64,
    max_cpu_seconds=2,
    timeout_seconds=5,
    allow_network=False,
    max_file_size_mb=1
)

sandbox = manager.create_sandbox("untrusted", config)
result = sandbox.execute(["python3", untrusted_script_path])
manager.cleanup_sandbox("untrusted")
```

### Batch Processing with Resource Limits

```python
# Process multiple files with resource constraints
for file_path in files_to_process:
    sandbox = manager.create_sandbox(f"process_{file_path.name}", config)
    
    result = sandbox.execute([
        "python3", "processor.py", str(file_path)
    ])
    
    if result.success:
        logger.info(f"Processed {file_path.name} in {result.duration}s")
    else:
        logger.error(f"Failed to process {file_path.name}: {result.error}")
    
    manager.cleanup_sandbox(f"process_{file_path.name}")
```

### Testing with Isolation

```python
# Run tests in isolated environment
test_config = SandboxConfig(
    max_memory_mb=1024,
    timeout_seconds=300,
    allow_network=True,  # May need network for package installation
    allowed_hosts=["pypi.org", "files.pythonhosted.org"]
)

sandbox = DockerSandbox(test_config, image="python:3.9")
sandbox.setup()

# Install dependencies
sandbox.execute("pip install -r requirements.txt")

# Run tests
result = sandbox.execute("pytest tests/ -v")

sandbox.cleanup()
```