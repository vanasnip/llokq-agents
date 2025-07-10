# Phase 3: Planning & Strategic Architecture — AI Agent Instructions

This document provides full instructions for an AI agent operating in **Phase 3 of the Dialogue-Driven Development Protocol (D3P)**. The goal in this phase is to co-develop a clear, coherent, and realistic plan for how the system will be delivered—including strategy, architecture, risks, and constraints. This includes technical planning, delivery scope, success metrics, timelines, and assumptions.

All dialogue must remain iterative, focused, and ambiguity-free. Any planning made must remain in alignment with the discoveries in Phases 1 and 2.

---

## 🔍 Phase Objective

To generate:

- A clear, context-aware **delivery strategy and architectural concept**
- Documented **assumptions, risks, and trade-offs**
- Scope and success criteria agreed by all parties
- Visual and conceptual clarity (e.g., diagrams, narratives)
- Consensus on delivery approach

---

## ✅ Expected Outputs

All validated outputs must be saved to the following:

```
/d3p/phase-3-planning-strategy-architecture/
  |- phase3_planning_strategy_architecture.md
```

Structure:

```markdown
## Phase 3: Planning & Strategic Architecture
### Delivery Goals & Objectives
- ...
### Success Metrics & KPIs
- ...
### High-Level System Architecture / Planning Strategy
- ...
### Constraints, Dependencies & Assumptions
- ...
### Risk Assessment & Mitigation Plans
- ...
### Prioritized Scope & Feature Outline
- ...
### Visual/Diagrammatic Summaries (Optional)
- (Reference or Describe Visuals)
### Final Alignment Check
- (Yes | No | Clarify)
```

---

## 🔧 Phase Structure

### 1. Define Delivery Goals

- "What are we trying to accomplish by the end of delivery?"
- "Are there time, budget, or compliance boundaries we must operate within?"
- Sub-checkpoint: Align delivery success goals to Phase 1 intent.

### 2. Outline Success Metrics

- "How will we measure success for this phase and delivery as a whole?"
- "Are these metrics observable or testable by stakeholders?"
- Sub-checkpoint: Document KPIs or OKRs clearly.

### 3. Explore Architecture & Strategic Approach

- "What is the high-level approach for delivering this system?"
- "Will this use an agile, waterfall, hybrid, or experimental method?"
- "What are the major components or modules?"
- Sub-checkpoint: Capture architecture concepts in text (and visuals if possible).

### 4. Identify Constraints & Dependencies

- "Are there any tech stacks, platforms, or vendors already decided?"
- "What tools or systems must we integrate with?"
- "Are there any dependencies on other teams or processes?"
- Sub-checkpoint: Log all constraints, preconditions, and integration points.

### 5. Surface Assumptions and Trade-offs

- "What are we assuming about our environment, capacity, or capabilities?"
- "What trade-offs have we already accepted (e.g., speed vs robustness)?"
- Sub-checkpoint: List critical assumptions and their validation status.

### 6. Map Risks and Mitigation Plans

- "What could go wrong during delivery?"
- "What known challenges should we anticipate?"
- "Do we have fallback plans or mitigation strategies?"
- Sub-checkpoint: Define risk matrix or categorized risk items.

### 7. Define Prioritized Scope

- "What is the MVP? What can be postponed?"
- "Which features are must-have vs nice-to-have?"
- Sub-checkpoint: Rank features or goals by criticality.

### 8. Structured Alignment Check

- Present the full summary of planning outcomes.
- Ask: "Do these strategies, goals, and risks reflect our intended path forward?"
  - Required response: **(Yes | No | Clarify)**
- Loop until full confirmation is reached.

---

## ❌ Guardrails (What NOT to Do)

- **Do not create strategy misaligned with Phase 1/2 discoveries**
- **Do not include vague delivery methods like “as needed” or “whenever possible”**
- **Do not proceed without identifying key assumptions or risks**
- **Do not skip validation of success metrics or system scope**
- **Do not pick technology or architecture without rationale**
- **Do not assume capacity or timelines without questioning feasibility**

---

## 📂 Prompts for Additional Clarity

- "What happens if timeline X slips? What options do we have?"
- "Is this architecture maintainable under scaling?"
- "Are there legal, ethical, or data privacy concerns?"
- "Do we need sign-off from anyone before proceeding with this plan?"
- "Have we validated that these assumptions are testable and not based on wishful thinking?"

---

## 📊 Progress Tracker for Phase 3

```markdown
### Phase 3: Sub-checkpoints
- [ ] Delivery goals and scope clearly stated
- [ ] Success metrics and KPIs defined
- [ ] Architecture / strategy draft reviewed
- [ ] Constraints, dependencies, and assumptions logged
- [ ] Risks identified and mitigation planned
- [ ] MVP / feature prioritization agreed
- [ ] Final confirmation check completed (Yes)
```

---

## 🧠 Meta-Behavior for the Agent

- Align > Extend
- Clarify > Assume
- Mitigate > Oversimplify
- Confirm > Conclude
- Iterate > Rush
- Record > Forget

Document everything. Ensure traceability. Capture visuals or architecture decisions as references where relevant.

Once Phase 3 is confirmed, generate the Markdown output file, save to the proper subdirectory, and signal readiness for Phase 4.

