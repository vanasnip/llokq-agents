#!/bin/bash
# Agent Switcher Script
# Usage: ./switch-agent.sh <agent-name>

# Check if agent name is provided
if [ $# -eq 0 ]; then
    echo "Error: Please provide an agent name"
    echo "Usage: ./switch-agent.sh <agent-name>"
    echo "Available agents: riley, aria, blake, quinn"
    exit 1
fi

AGENT_NAME=$1
AGENT_DIR="/Users/ivan/DEV_/agents"
ACTIVE_DIR="$AGENT_DIR/active_project"

# Convert agent name to lowercase
AGENT_NAME_LOWER=$(echo "$AGENT_NAME" | tr '[:upper:]' '[:lower:]')

# Map short names to full agent names
case $AGENT_NAME_LOWER in
    "riley")
        FULL_NAME="requirement_agent"
        LITE_PROFILE="riley_lite.yaml"
        ;;
    "aria")
        FULL_NAME="api_architect"
        LITE_PROFILE="aria_lite.yaml"
        ;;
    "blake")
        FULL_NAME="backend_engineer"
        LITE_PROFILE="blake_lite.yaml"
        ;;
    "quinn")
        FULL_NAME="qa_engineer"
        LITE_PROFILE="quinn_lite.yaml"
        ;;
    *)
        echo "Error: Unknown agent '$AGENT_NAME'"
        echo "Available agents: riley, aria, blake, quinn"
        exit 1
        ;;
esac

echo "🎭 Switching to $AGENT_NAME_LOWER agent..."

# Load compressed profile
if [ -f "$ACTIVE_DIR/context/$LITE_PROFILE" ]; then
    echo "Loading compressed profile from: $LITE_PROFILE"
    cp "$ACTIVE_DIR/context/$LITE_PROFILE" "$ACTIVE_DIR/current_agent.md"
    
    # Add activation timestamp
    echo -e "\n---\n## Activation Details\n" >> "$ACTIVE_DIR/current_agent.md"
    echo "**Activated**: $(date '+%Y-%m-%d %H:%M:%S')" >> "$ACTIVE_DIR/current_agent.md"
    echo "**Full Agent Name**: $FULL_NAME" >> "$ACTIVE_DIR/current_agent.md"
    
    # Try to load additional context from full agent definition if available
    if [ -f "$AGENT_DIR/dev_agents/agents.yaml" ]; then
        echo -e "\n## Additional Context from Full Profile\n" >> "$ACTIVE_DIR/current_agent.md"
        grep -A 15 "^$FULL_NAME:" "$AGENT_DIR/dev_agents/agents.yaml" >> "$ACTIVE_DIR/current_agent.md" 2>/dev/null || echo "Full profile not found"
    fi
    
    echo "✅ Agent context loaded successfully!"
    echo "📄 Check: $ACTIVE_DIR/current_agent.md"
    
    # Update phase status
    sed -i '' "s/\*\*Active Agent\*\*: .*/\*\*Active Agent\*\*: $AGENT_NAME_LOWER/" "$ACTIVE_DIR/phase_status.md" 2>/dev/null || \
    sed -i "s/\*\*Active Agent\*\*: .*/\*\*Active Agent\*\*: $AGENT_NAME_LOWER/" "$ACTIVE_DIR/phase_status.md"
    
else
    echo "Error: Compressed profile not found for $AGENT_NAME"
    exit 1
fi

echo ""
echo "💡 Next steps:"
echo "1. Review the agent profile in current_agent.md"
echo "2. Use the activation template to start the agent"
echo "3. Begin work on the current phase task"