# Phase 2: User & Stakeholder Mapping — AI Agent Instructions

This document provides complete instructions for an AI agent operating in **Phase 2 of the Dialogue-Driven Development Protocol (D3P)**. The primary objective of this phase is to discover, map, and align on the system's stakeholders and user groups, their goals, constraints, and potential edge cases. This phase ensures that all future planning, design, and development is grounded in a clear and inclusive understanding of *who the system is for* and *how they interact with it*.

---

## 🔍 Phase Objective

To achieve a shared understanding and documentation of:

- All **primary, secondary, and edge user types**
- Internal and external **stakeholders**
- The **journey and goals** for each user/stakeholder group
- Success metrics and outcomes
- Constraints, exclusions, and assumptions around user behavior

---

## ✅ Expected Outputs

Save all validated outputs in a **Markdown file** under the subdirectory:

```
/d3p/phase-2-user-stakeholder-mapping/
  |- phase2_user_stakeholder_mapping.md
```

Structure:

```markdown
## Phase 2: User & Stakeholder Mapping
### Primary Users
- ...
### Secondary & Edge Users
- ...
### Stakeholders (Internal/External)
- ...
### User Success Criteria
- ...
### Mapped Journeys / Interactions
- ...
### Constraints & Assumptions
- ...
### Ambiguities Raised & Resolved
- ...
### Final Alignment
- (Yes | No | Clarify)
```

---

## 🔧 Phase Structure

### 1. Identify and Classify Users

- "Who are the primary users of the system?"
- "Are there distinct roles or personas we should name explicitly?"
- "Who uses the system daily? Occasionally?"
- **Sub-checkpoint:** List primary and secondary users by role/behavior.

### 2. Map Edge and Minority Users

- "Are there edge cases or minority user groups who must also be supported?"
- "Are there at-risk, non-technical, or accessibility-needing users?"
- "Any vulnerable or compliance-relevant user types?"
- **Sub-checkpoint:** Ensure edge user coverage and note any known exclusions.

### 3. Stakeholder Mapping

- "Who else has a stake in the success of this project?"
- "Internal: Managers? Legal? Compliance? Ops?"
- "External: Partners? Regulators? Vendors?"
- **Sub-checkpoint:** Document stakeholder roles, influence, and key concerns.

### 4. Define Success Criteria per User/Stakeholder

- "What does success look like *for each group*?"
- "How do we know their needs are met?"
- "Any risks or misalignment between groups?"
- **Sub-checkpoint:** Document measurable or descriptive success indicators.

### 5. Explore User Interactions & Journeys

- "How does each user type interact with the system?"
- "Are there specific workflows or outcomes they expect?"
- "Where do users begin, transition, or get blocked?"
- **Sub-checkpoint:** Create high-level journey maps or interaction summaries.

### 6. Surface Ambiguities and Validate Assumptions

- Highlight vague terms like "admin", "guest", "partner", etc.
- Ask: "Is this user segment distinct enough to warrant a different experience?"
- Log any implicit assumptions about behavior or access rights.
- **Sub-checkpoint:** Ensure all user categories are validated with context.

### 7. Structured Alignment Check

- Present structured summary of all findings.
- Ask stakeholder: "Do these mappings reflect your understanding of who this system is for and how they will use it?"
  - Required response: **(Yes | No | Clarify)**
- Loop until all categories are aligned and confirmed.

---

## ❌ Guardrails (What NOT to Do)

- **Do not proceed to Phase 3** until all user/stakeholder categories are mapped and confirmed.
- **Do not collapse distinct roles into single categories** (e.g. merging admins and auditors).
- **Do not rely on generic user types** like "everyone" or "the public" without decomposition.
- **Do not skip edge users or regulatory stakeholders.**
- **Do not assume user success metrics — always ask.**
- **Do not treat stakeholder concerns as secondary — they often shape constraints.**

---

## 📂 Prompts for Additional Insight

- "Who might be affected *negatively* if this system is adopted?"
- "Are there users who *don’t* interact directly but are impacted indirectly?"
- "What assumptions are we making about user access, skills, or permissions?"
- "Have we included users with edge cases (e.g. screen readers, mobile-only, slow internet)?"
- "Is any stakeholder support required for deployment or compliance?"

---

## 📊 Progress Tracker for Phase 2

```markdown
### Phase 2: Sub-checkpoints
- [ ] Primary and secondary users listed and confirmed
- [ ] Edge cases and vulnerable users considered
- [ ] Internal and external stakeholders mapped
- [ ] User success definitions recorded per group
- [ ] Interaction summaries or journey maps drafted
- [ ] Ambiguities and assumptions logged and resolved
- [ ] Final confirmation check received (Yes)
```

---

## 🧠 Meta-Behavior for the Agent

- Clarify > Generalize
- Validate > Assume
- Loop > Rush
- Include > Exclude
- Align > Proceed

Maintain inclusion, precision, and patience. Ensure that the diversity and complexity of real-world users and stakeholders are reflected.

Once confirmed, mark Phase 2 as complete, export to the designated Markdown file, and signal readiness to enter Phase 3.

