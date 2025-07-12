# Quick Start Guide - Phase 1 Implementation

## 🚀 Getting Started

You now have a minimal agent system ready for your first pilot project!

### What's Been Created

1. **Directory Structure**
   ```
   /active_project/
   ├── context/           # Compressed agent profiles (4 agents)
   ├── handoffs/         # For agent transition logs
   ├── artifacts/        # For agent outputs
   ├── current_agent.md  # Current active agent
   └── phase_status.md   # Phase tracking
   ```

2. **4 Pilot Agents** (compressed profiles ready)
   - **Riley** - Requirements Discovery
   - **Aria** - API Design
   - **Blake** - Backend Implementation
   - **Quinn** - Quality Assurance

3. **Tools & Templates**
   - `switch-agent.sh` - Script to switch between agents
   - Agent activation template
   - Handoff templates (quick & detailed)
   - Phase status tracker

4. **Pilot Project**
   - Task Management API (see `/artifacts/project_brief.md`)

## 🎯 How to Run Your First Project

### Step 1: Start with Requirements (Riley)

```bash
# Switch to Riley
cd /Users/ivan/DEV_/agents
./switch-agent.sh riley

# Review the agent profile
cat active_project/current_agent.md

# In your AI conversation, use the activation template:
"I need you to become the Riley agent. Your identity is 'I discover what truly matters by asking why, listening deeply, and translating needs into clear specifications'. Your task is to gather requirements for the Task Management API described in project_brief.md"
```

### Step 2: Hand off to API Design (Aria)

```bash
# After Riley completes requirements
./switch-agent.sh aria

# Create a handoff document
# Use the quick handoff template from handoff_template.md
```

### Step 3: Implementation (Blake)

```bash
# After Aria completes API design
./switch-agent.sh blake
```

### Step 4: Testing (Quinn)

```bash
# After Blake completes implementation
./switch-agent.sh quinn
```

## 📊 Tracking Progress

1. **Update Phase Status**: Edit `phase_status.md` as you progress
2. **Document Handoffs**: Save in `/handoffs/` directory
3. **Store Outputs**: All agent outputs go in `/artifacts/`

## 💡 Tips for Success

1. **Keep It Simple**: This is a pilot - don't over-engineer
2. **Time Box**: Try to stick to estimated times
3. **Document Pain Points**: Note what's working and what's not
4. **Use Templates**: They're there to help maintain consistency

## 🔧 Common Commands

```bash
# Switch agent
./switch-agent.sh <riley|aria|blake|quinn>

# Check current agent
cat active_project/current_agent.md

# View phase status
cat active_project/phase_status.md

# List artifacts
ls -la active_project/artifacts/
```

## 📝 After Completion

1. Review total time spent vs estimates
2. Document top 3 learnings
3. Identify biggest pain points
4. Plan optimizations for Phase 2

---

**Ready to start?** Switch to Riley and begin gathering requirements for the Task Management API!