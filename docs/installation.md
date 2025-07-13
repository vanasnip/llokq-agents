# Installation Guide

This guide provides detailed instructions for installing the Unified D3P-SuperClaude Agent System.

## Prerequisites

- Python 3.8 or higher
- Git
- pip (Python package manager)
- Virtual environment support (recommended)

## Installation Options

### Option 1: Standard Installation (Recommended)

This is the recommended approach for most users.

```bash
# Clone the repository
git clone <repository-url>
cd agents

# Install in editable mode
pip install -e .

# Run initial setup
unified-agents setup
```

The setup command will:
- Create necessary directories (`~/.claude/`)
- Copy default configuration files
- Validate the installation
- Generate agent configurations

### Option 2: Global Installation

For system-wide installation:

```bash
# Install directly from git
pip install git+https://github.com/yourusername/agents.git

# Run setup
unified-agents setup

# Verify installation
unified-agents --version
```

### Option 3: Development Installation

For contributors and developers:

```bash
# Clone the repository
git clone <repository-url>
cd agents

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests to verify
pytest tests/
```

### Option 4: Docker Installation

Using Docker for isolated environment:

```bash
# Clone the repository
git clone <repository-url>
cd agents

# Build Docker image
docker build -t unified-agents .

# Run container
docker run -it unified-agents

# Or with volume mounting for persistence
docker run -it -v ~/.claude:/root/.claude unified-agents
```

## Post-Installation Setup

### 1. Verify Installation

```bash
# Check version
unified-agents --version

# Test basic functionality
unified-agents demo

# List available agents
unified-agents agents
```

### 2. Configure Environment

The system uses these environment variables (optional):

```bash
# Set custom config directory
export CLAUDE_CONFIG_DIR=~/.claude

# Set log level
export UNIFIED_LOG_LEVEL=INFO

# Enable debug mode
export UNIFIED_DEBUG=1
```

Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
# Unified Agents
export PATH="$PATH:$HOME/.local/bin"
alias ua="unified-agents"
```

### 3. First Run

On first run, the system will:

1. Create configuration directory
2. Generate default configurations
3. Convert agent definitions
4. Set up workflow templates

```bash
# Initialize system
unified-agents setup

# Start interactive mode
unified-agents interactive
```

## Configuration Files

After setup, these files are created in `~/.claude/`:

```
~/.claude/
├── agents.yml         # Agent definitions
├── workflows.yml      # Workflow configurations
├── settings.yml       # System settings
└── logs/             # Application logs
```

## Troubleshooting

### Python Version Issues

```bash
# Check Python version
python --version

# If needed, use specific version
python3.8 -m pip install -e .
```

### Permission Errors

```bash
# Install for current user only
pip install --user -e .

# Or use sudo (not recommended)
sudo pip install -e .
```

### Import Errors

```bash
# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/agents"

# Or install in development mode
pip install -e .
```

### Missing Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# For development
pip install -r requirements-dev.txt
```

## Upgrading

### From Git

```bash
cd agents
git pull origin main
pip install -e . --upgrade

# Run migrations if needed
unified-agents migrate --apply
```

### From Package

```bash
pip install --upgrade unified-agents

# Check for schema updates
unified-agents migrate --status
```

## Uninstalling

### Complete Removal

```bash
# Uninstall package
pip uninstall unified-agents

# Remove configuration (optional)
rm -rf ~/.claude

# Remove repository (if cloned)
rm -rf /path/to/agents
```

### Keep Configuration

```bash
# Just uninstall package
pip uninstall unified-agents

# Configuration remains in ~/.claude
```

## Platform-Specific Notes

### macOS

- Ensure Xcode Command Line Tools are installed
- May need to install Python via Homebrew
- Use `python3` instead of `python`

### Linux

- Install Python development headers: `sudo apt-get install python3-dev`
- May need to install pip: `sudo apt-get install python3-pip`
- Consider using system package manager

### Windows

- Use PowerShell or WSL for best experience
- Path separator is `\` instead of `/`
- Virtual environment activation: `venv\Scripts\activate.bat`

## Advanced Setup

### Custom Configuration Location

```python
# In your code
from unified.core import set_config_dir
set_config_dir("/custom/path")
```

### Integration with IDEs

#### VS Code

Add to `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.terminal.activateEnvironment": true
}
```

#### PyCharm

1. File → Settings → Project → Python Interpreter
2. Add Interpreter → Existing Environment
3. Select `venv/bin/python`

## Next Steps

After installation:

1. Read the [Command Reference](commands.md)
2. Explore the [Agent Catalog](agents.md)
3. Try the [Tutorial](tutorial.md)
4. Learn about [Workflows](workflows.md)

## Getting Help

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review [GitHub Issues](https://github.com/yourusername/agents/issues)
3. Join our [Discord Server](https://discord.gg/your-invite)
4. Email support: support@your-domain.com