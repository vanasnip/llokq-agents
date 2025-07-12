# Active Project Directory

This directory manages the current active project state for the agent system.

## Structure

- `current_agent.md` - Tracks the currently active agent
- `phase_status.md` - Tracks D3P phase progress
- `handoffs/` - Agent transition logs
- `artifacts/` - Output documents from agents
- `context/` - Compressed agent profiles for quick loading

## Usage

1. Start a new project by updating `phase_status.md`
2. Switch agents using the `switch-agent.sh` script
3. Document handoffs in the `handoffs/` directory
4. Store all outputs in `artifacts/`

## Current Project

**Project**: Simple CRUD API Pilot
**Status**: Phase 1 - Requirements Discovery
**Active Agent**: None (ready to start)