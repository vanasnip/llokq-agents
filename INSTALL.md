# Installation Guide

## 🚀 Quick Install (2 minutes)

```bash
# Clone and install
git clone <repository-url>
cd agents
pip install -e .

# Start using immediately
unified-agents interactive
```

That's it! The system automatically sets up everything on first run.

## 📦 Installation Options

### 1. User Install (Recommended)
Best for most users who want to use the agents.

```bash
pip install -e .
unified-agents interactive
```

### 2. Developer Install
For those who want to modify or extend the system.

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install with development dependencies
pip install -e .

# Run tests and demos
unified-agents demo
```

### 3. Global Install
Install system-wide (requires appropriate permissions).

```bash
sudo pip install .
```

## 🔧 What Gets Installed

- **Command Line Tool**: `unified-agents` (or `ua` for short)
- **Python Package**: `unified` module
- **Agent Definitions**: Automatically configured in `~/.claude/agents.yml`
- **Dependencies**: PyYAML, Click, Rich (terminal UI)

## 🎯 First Run

On first run, the system will:
1. ✅ Automatically convert all agent definitions
2. ✅ Create configuration directory at `~/.claude/`
3. ✅ Set up all 15 specialized agents
4. ✅ Initialize D3P phases

## 🚨 Troubleshooting

### "Command not found"
```bash
# Ensure pip scripts are in PATH
export PATH="$HOME/.local/bin:$PATH"
```

### "No module named unified"
```bash
# Reinstall in development mode
pip install -e .
```

### "Permission denied"
```bash
# Use user install instead
pip install --user -e .
```

## ✅ Verify Installation

```bash
# Check installation
unified-agents --version

# List agents
unified-agents agents

# Run demo
unified-agents demo
```

## 🗑️ Uninstall

```bash
# Remove package
pip uninstall unified-agents

# Remove configuration (optional)
rm -rf ~/.claude/agents.yml
```