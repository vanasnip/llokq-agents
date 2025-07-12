# Pilot Project Brief: Task Management API

## Overview
Build a simple Task Management API to validate the agent system workflow. This is a CRUD API with enough complexity to test all 4 agents but simple enough to complete in Phase 1.

## Core Features
1. **Tasks** - Basic CRUD operations
   - Create a new task
   - List all tasks (with pagination)
   - Get a specific task
   - Update a task
   - Delete a task

2. **Task Properties**
   - id (auto-generated UUID)
   - title (required, max 200 chars)
   - description (optional, max 1000 chars)
   - status (enum: todo, in_progress, done)
   - priority (enum: low, medium, high)
   - created_at (timestamp)
   - updated_at (timestamp)

3. **Additional Requirements**
   - Input validation
   - Proper error responses
   - Basic filtering by status
   - Sort by created_at or priority

## Success Criteria
- All CRUD operations working
- Proper HTTP status codes
- Consistent API design
- 90%+ test coverage
- Response time < 200ms

## Out of Scope (for pilot)
- Authentication
- User management
- Task assignment
- Due dates
- Comments/attachments

## Technology Stack (Suggested)
- Language: Python or Node.js (agent's choice)
- Framework: FastAPI/Express (agent's choice)
- Database: PostgreSQL or SQLite (agent's choice)
- Testing: pytest/jest (agent's choice)

---

This pilot is designed to be completed in 4-6 hours across all 4 agents.