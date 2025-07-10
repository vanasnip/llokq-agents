# Phase 4: Functional Decomposition & Capability Mapping — AI Agent Instructions

This document defines a complete instruction set for an AI agent operating in **Phase 4 of the Dialogue-Driven Development Protocol (D3P)**. This phase translates stakeholder goals and strategies into discrete, decomposed functional components. The aim is to explicitly uncover the system's functional structure, identify interdependencies, define critical paths, and surface hidden complexity. Every function discussed should link directly to user needs and architectural alignment from Phases 1–3.

---

## 🔍 Phase Objective

To achieve a complete breakdown of:

- Core system **capabilities** and **functional groupings**
- Functional **requirements** mapped to users/stakeholders
- Prioritization of features (core vs. optional)
- Sequence of dependencies
- Ambiguities and risk areas in functionality

---

## ✅ Expected Outputs

All validated and aligned outputs must be stored as follows:

```
/d3p/phase-4-functional-decomposition/
  |- phase4_functional_decomposition.md
```

Markdown Structure:

```markdown
## Phase 4: Functional Decomposition & Capability Mapping
### Functional Capability Groups
- ...
### Atomic Functional Requirements
- ...
### Feature Dependencies & Sequences
- ...
### Feature Priority Table (MVP vs. Later)
- ...
### Mapped Roles to Functions
- ...
### Known Conflicts, Ambiguities, or Edge Cases
- ...
### Final Alignment Check
- (Yes | No | Clarify)
```

---

## 🔧 Phase Structure

### 1. Identify Capability Clusters

- "What are the major groups of functionality needed to support the delivery goals?"
- "Which groups serve which user needs?"
- **Sub-checkpoint**: Create and validate top-level groupings (e.g., User Management, Reporting, Messaging).

### 2. Decompose Into Atomic Functional Requirements

- "What specific actions must the system support within each capability cluster?"
- "How should this function behave in typical and edge cases?"
- **Sub-checkpoint**: List all discrete, testable functional requirements.

### 3. Map Interdependencies and Sequences

- "Which functions must precede others (e.g., registration before commenting)?"
- "Are there circular or blocking dependencies to untangle?"
- **Sub-checkpoint**: Draft a basic functional flow or dependency map.

### 4. Prioritize Functionality

- "Which functions are part of the MVP?"
- "Which can be deferred to later stages or releases?"
- **Sub-checkpoint**: Build a MVP vs. Post-MVP table.

### 5. Map Functions to Roles/Users

- "Who will use each function?"
- "Are some roles blocked or restricted from this function?"
- **Sub-checkpoint**: Create a role-function matrix.

### 6. Identify Ambiguities & Conflicts

- Surface functional overlaps (e.g., Admin vs. Moderator powers)
- Detect overgeneralizations ("User can do X" without specifying scope or guardrails)
- **Sub-checkpoint**: Log unresolved questions or assumptions

### 7. Structured Alignment Check

- Present completed decomposition
- Ask: "Does this reflect your intended system behavior and priorities?"
  - Response: **(Yes | No | Clarify)**
- Iterate until alignment is confirmed

---

## ❌ Guardrails (What NOT to Do)

- **Do not skip decomposition for vague feature labels** (e.g., "analytics", "AI integration")
- **Do not group unrelated functions into single capability blocks**
- **Do not mix UI/UX assumptions with functional logic without discussion**
- **Do not assign functionality without linking to user needs or roles**
- **Do not ignore edge cases or exceptions**
- **Do not proceed with unresolved capability conflicts**

---

## 📂 Prompts for Additional Insight

- "Is this function universal or conditional based on role, time, state, or permissions?"
- "How would this capability be tested or validated?"
- "Does any feature imply another capability that we haven't explicitly listed?"
- "What happens if this function fails, times out, or gets unexpected input?"
- "Do any features overlap in a way that could create confusion or conflict?"

---

## 📊 Progress Tracker for Phase 4

```markdown
### Phase 4: Sub-checkpoints
- [ ] Capability clusters identified and confirmed
- [ ] Atomic functional requirements listed and validated
- [ ] Functional dependencies and flows mapped
- [ ] MVP features separated from later priorities
- [ ] User-role-function matrix built
- [ ] Conflicts and ambiguities logged and resolved
- [ ] Final alignment check completed (Yes)
```

---

## 🧠 Meta-Behavior for the Agent

- Decompose > Generalize
- Validate > Bundle
- Trace > Assume
- Iterate > Proceed
- Clarify > Collapse

All functional structure must trace back to user value, stakeholder priority, and strategic feasibility. When in doubt, ask. When confident, summarize. When done, align.

Once validated, save the results as a Markdown file under the specified directory and signal readiness for Phase 5.

