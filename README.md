# Unified D3P-SuperClaude Agent System

A comprehensive AI agent development system that combines D3P's rich agent definitions with SuperClaude's elegant command structure. This system provides 15+ specialized AI agents for software development, from requirements gathering through deployment.

## 🌟 Features

- **15 Specialized AI Agents**: Each with unique personalities, decision frameworks, and expertise
- **Elegant Command System**: Simple, intuitive commands like `/code --backend --frontend`
- **Multi-Agent Workflows**: Pre-built workflows for feature development, bug investigation, and security audits
- **D3P Phase Management**: 10-phase development protocol from vision to documentation
- **Rich Agent Context**: Each agent brings core beliefs, success metrics, and problem-solving approaches
- **MCP Integration**: Agent-specific tool preferences (filesystem, shell, memory, etc.)

## 📋 Prerequisites

- Python 3.8+
- Git
- Basic understanding of command-line interfaces

## 🚀 Quick Start

### Option 1: Install from Package (Recommended)

```bash
# Clone and install
git clone <repository-url>
cd agents
pip install -e .

# First time setup (automatic)
unified-agents setup

# Start using
unified-agents interactive
```

### Option 2: Install Globally

```bash
# Install directly from git
pip install git+https://github.com/yourusername/agents.git

# Run setup
unified-agents setup

# Start using
unified-agents interactive
```

### Option 3: Development Mode

```bash
# Clone the repository
git clone <repository-url>
cd agents

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Start developing
unified-agents demo
```

That's it! The system automatically handles agent configuration on first run.

## 🤖 Available Agents

### Design Agents (5)
- **aura** - Accessibility & Usability Review Assistant
- **motion_maestra** - AI Motion Design Strategist  
- **chromatic_architect** - Brand Theme Development Specialist
- **layout_loom** - AI Design Layout Specialist
- **riley** - Requirements Discovery Specialist

### Architecture Agents (2)
- **architect** - System Architecture Specialist
- **api** - API Design Specialist

### Development Agents (4)
- **backend** - Backend Development Specialist
- **frontend** - Frontend Architecture Specialist
- **data** - Data Engineering Specialist
- **mobile** - Mobile Development Specialist

### Quality Agents (3)
- **qa** - Quality Assurance Specialist
- **security** - Security Engineering Specialist
- **performance** - Performance Engineering Specialist

### Operations Agents (1)
- **devops** - DevOps & Platform Engineering Specialist

## 💻 Usage

After installation, you can use the `unified-agents` command (or `ua` for short):

```bash
# Quick commands
unified-agents agents       # List all available agents
unified-agents demo         # Run a demonstration
unified-agents interactive  # Start interactive mode
unified-agents status       # Show current phase
unified-agents info backend # Get agent details

# Or use the short alias
ua agents
ua interactive
ua demo
```

### Interactive Mode Commands

Once in interactive mode, use these commands:

```bash
# Agent commands
/agent --list               # List all available agents
/agent --info backend       # Get detailed info about an agent

# Execute commands with specific agents
/code --backend --frontend
/design --aura --layout_loom
/test --qa --security
/analyze --architect
/deploy --devops
```

### Workflow Commands

```bash
# Start a workflow
/workflow feature    # Feature development workflow
/workflow bug       # Bug investigation workflow
/workflow security  # Security audit workflow

# Check workflow status
/workflow --status

# Execute next step
/workflow --next
```

### Phase Management

```bash
# Show current D3P phase
/phase --current

# Move to next phase
/phase --next

# Jump to specific phase
/phase --goto 3
```

### Multi-Agent Operations

```bash
# Activate multiple agents
/team --activate "backend,frontend,qa"

# Perform agent handoff
/agent --handoff
```

## 🔄 Workflows

### Feature Development Workflow
1. **Requirements Discovery** (riley, architect)
2. **Architecture Design** (architect, api)
3. **UI/UX Design** (layout_loom, chromatic_architect, aura)
4. **Implementation** (backend, frontend)
5. **Testing** (qa, security, performance)
6. **Deployment** (devops)

### Bug Investigation Workflow
1. **Triage** (qa)
2. **Root Cause Analysis** (backend, frontend, architect)
3. **Fix Implementation** (backend, frontend)
4. **Verification** (qa)
5. **Deployment** (devops)

### Security Audit Workflow
1. **Threat Modeling** (security, architect)
2. **Vulnerability Scanning** (security)
3. **Remediation** (security, backend, devops)
4. **Verification** (security, qa)

## 📁 Project Structure

```
agents/
├── unified/                    # Main unified system
│   ├── agents/                # Agent management
│   │   ├── schema.py         # Agent data model
│   │   └── manager.py        # Agent loading/activation
│   ├── core/                  # Core components
│   │   ├── command_parser.py # Command parsing
│   │   ├── command_executor.py # Command execution
│   │   └── phase_manager.py  # D3P phase management
│   ├── workflows/             # Workflow engine
│   │   └── engine.py         # Workflow orchestration
│   ├── cli.py                # Interactive CLI
│   └── demo.py               # Demonstration script
├── design_agents/             # Original design agent definitions
├── dev_agents/               # Original dev agent definitions
├── d3p/                      # D3P protocol definitions
└── orchestration/            # Workflow templates
```

## 🎯 D3P Phases

The system follows the Dialogue-Driven Development Protocol (D3P) with 10 phases:

1. **Vision & Requirements** - Establish project goals
2. **Architecture & Planning** - Design system architecture
3. **Design System** - Create UI/UX designs
4. **Development Setup** - Configure development environment
5. **Core Implementation** - Build core features
6. **Testing & Security** - Comprehensive testing
7. **Refinement** - Optimize and polish
8. **Deployment Preparation** - Prepare for production
9. **Production Release** - Deploy to production
10. **Documentation & Handoff** - Complete documentation

## 🛠️ Configuration

### Agent Configuration
Agents are defined in `~/.claude/agents.yml` with:
- Identity and role
- Core beliefs and values
- Decision frameworks
- Success metrics
- MCP tool preferences
- Compatible agents for collaboration

### Custom Workflows
Create new workflows by adding to `workflows/engine.py`:
```python
custom_workflow = Workflow(
    name="custom_workflow",
    type="custom",
    description="Your custom workflow",
    steps=[
        WorkflowStep(
            name="step_name",
            agents=["agent1", "agent2"],
            command="/command --agent1 --agent2",
            required_outputs=["output.md"]
        )
    ]
)
```

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure PYTHONPATH is set
   export PYTHONPATH=/path/to/agents
   ```

2. **Agent Not Found**
   ```bash
   # Regenerate agent configuration
   python scripts/convert_agents.py
   cp config/agents.yml ~/.claude/agents.yml
   ```

3. **Command Not Recognized**
   ```bash
   # Commands must start with /
   /code --backend  # Correct
   code --backend   # Incorrect
   ```

## 🚧 Future Enhancements

- [ ] Real command execution integration
- [ ] Persistent workflow state
- [ ] Web-based UI
- [ ] Custom agent creation
- [ ] Plugin system for extensions
- [ ] Integration with development tools

## 📄 License

[Your License Here]

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation in `/docs`
- Review the demo script for examples

---

Built with ❤️ using the D3P methodology and inspired by SuperClaude's elegance.