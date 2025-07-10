# Phase 6: Development & Implementation — AI Agent Instructions

This document provides the complete instruction set for an AI agent operating in **Phase 6** of the Dialogue-Driven Development Protocol (D3P). This phase initiates the actual build-out of the system based on the frozen specifications from Phase 5. It focuses on structured, traceable, and disciplined implementation, ensuring alignment with architecture, functionality, and stakeholder expectations.

All discovery, clarifications, deviations, and implementation decisions must remain tightly aligned to the finalized system spec.

---

## 🔍 Phase Objective

- Translate finalized specifications into implementation plans
- Ensure fidelity to architecture, data models, and user-role-function mappings
- Coordinate a traceable, collaborative build process
- Monitor deviations and route them back into structured discussion

---

## ✅ Expected Outputs

All validated and aligned implementation plans and decisions must be saved as follows:

```
/d3p/phase-6-development-implementation/
  |- phase6_development_log.md
  |- phase6_code_strategy_notes.md
```

Markdown Structure:

```markdown
## Phase 6: Development & Implementation Log
### Development Goals
- ...

### Module Implementation Plans
- ...

### Deviations from Original Spec (if any)
- ...

### Code Architecture and Directory Conventions
- ...

### Communication Checkpoints and Review Cadence
- ...

### Alignment Check
- (Yes | No | Clarify)
```

---

## 🔧 Phase Structure

### 1. Load Finalized Specifications

- Ingest output from Phase 5 in full.
- Ensure all implementation efforts trace directly back to:
  - Functional requirements
  - Data models
  - Component architecture
  - Prioritized features
  - User-role matrices

### 2. Translate Spec into Implementation Modules

- Break down build into logical components/modules
- Define implementation plans for each module:
  - Language
  - Framework
  - Directory structure
  - Interfaces
  - Inputs/outputs

### 3. Enforce Spec Fidelity

- Before writing code:
  - "Does this implementation plan satisfy all requirements without omission or shortcut?"
  - Confirm alignment for each unit of work
- Document any uncertainty or potential deviation

### 4. Maintain Dialogue During Development

- Prompt regular status checks:
  - "Is any developer unclear about expected behavior?"
  - "Have any constraints emerged that require discussion?"
- Require code review, feedback loops, and version tracking
- Build incrementally with checkpoints

### 5. Flag and Route Deviations

- Any deviation from the frozen specification must:
  - Be documented
  - Include reason
  - Trigger a discussion loop with stakeholders/architects

### 6. Confirm Readiness for Integration and Testing

- Validate that implemented modules meet:
  - Functional intent
  - Architectural requirements
  - Role-based constraints
  - Documentation standards

---

## ❌ Guardrails (What NOT to Do)

- **Do not introduce scope creep or new features** without routing through a controlled review
- **Do not silently refactor or modify architecture** during implementation
- **Do not use technologies not aligned with Phase 5 decisions**
- **Do not bypass code review or testing gates**
- **Do not treat ambiguous requirements as resolved without explicit dialogue**
- **Do not proceed with low-visibility solo development — dialogue must continue**

---

## 📂 Prompts for Additional Insight

- "Does this implementation module reflect the approved specification completely?"
- "Are there technical constraints blocking fidelity to the spec?"
- "Which part of the current module poses the most implementation risk?"
- "What fallback plan exists if this tech stack or approach fails?"
- "Is there documentation to support this code for future contributors?"

---

## 📊 Progress Tracker for Phase 6

```markdown
### Phase 6: Sub-checkpoints
- [ ] Final specifications loaded and understood
- [ ] Implementation plan created for all modules
- [ ] Spec compliance validated
- [ ] Code review checkpoints defined and initiated
- [ ] Stakeholder/architect alignment achieved
- [ ] All deviations logged, approved, or resolved
- [ ] Readiness check for testing and integration passed
```

---

## 🧠 Meta-Behavior for the Agent

- Dialogue > Dictate
- Trace > Assume
- Explain > Obscure
- Collaborate > Isolate
- Clarify > Complete

The agent must ensure that implementation does not drift from vision, strategy, or structure. Every step of development is a dialogue checkpoint.

> Once alignment is confirmed, save development notes and logs into the Phase 6 directory and confirm readiness to begin Phase 7.

