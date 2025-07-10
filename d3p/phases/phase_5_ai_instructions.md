# Phase 5: Review, Feedback & Specification Finalization — AI Agent Instructions

This document provides the complete instruction set for an AI agent operating in **Phase 5** of the Dialogue-Driven Development Protocol (D3P). This phase finalizes the outputs of Phases 1–4 by collecting structured feedback, addressing any unresolved ambiguity, validating assumptions, and preparing a stable, version-controlled specification set. It is the final phase before implementation begins.

---

## 🔍 Phase Objective

- Conduct **structured review sessions** with stakeholders
- Resolve any open questions, flagged assumptions, or missing information from previous phases
- Validate that all outputs are clear, unambiguous, and traceable to stakeholder goals
- Create **finalized specification documents** that act as the authoritative source for downstream development

---

## ✅ Expected Outputs

All finalized and aligned outputs must be saved as follows:

```
/d3p/phase-5-review-finalization/
  |- phase5_finalized_specifications.md
```

Markdown Structure:

```markdown
## Phase 5: Review, Feedback & Final Specification
### Confirmed Inputs from Previous Phases
- [Summary of what was carried forward from Phases 1–4]

### Addressed Ambiguities and Final Clarifications
- [List of previously unclear items and their resolutions]

### Feedback Incorporated
- [Stakeholder or user feedback and resulting changes]

### Specification Freeze: Approved System Description
- [Formal, validated description of intended system behavior and components]

### Final Alignment Check
- (Yes | No | Clarify)
```

---

## 🔧 Phase Structure

### 1. Load Phase Artifacts

- Load summaries and final artifacts from:
  - Phase 1: Intent Alignment
  - Phase 2: Strategy & Stakeholder Mapping
  - Phase 3: System Architecture & Constraints
  - Phase 4: Functional Decomposition

### 2. Perform Structured Review with Stakeholders

- Walk through each major section and prompt:
  - "Do you agree with this outcome as stated?"
  - "Is this assumption still valid?"
  - "Have priorities changed since this was documented?"
- Use: **(Yes | No | Clarify)** for each response.
- Collect unresolved flags and initiate resolution discussions.

### 3. Resolve Misalignments and Clarify Assumptions

- Document all previously open or fuzzy requirements.
- Engage stakeholders to verify accuracy or provide additional details.
- Finalize decision logs on edge cases or disputed functionality.

### 4. Incorporate All Feedback

- Any feedback received from users, stakeholders, reviewers, or validators must be synthesized.
- Adjust the Phase 4 output or design as needed.
- Track changes explicitly in a changelog section if major.

### 5. Perform Final Alignment Check

- Present the complete specification and state:
  - "Does this reflect the correct and full picture of what is to be built?"
- Only proceed to next phase when response is: **Yes**

### 6. Save Finalized Output

- Write the complete, version-controlled specification to Markdown file.
- Store in Phase 5 directory.
- Signal completion and readiness for implementation entry point (Phase 6).

---

## ❌ Guardrails (What NOT to Do)

- **Do not proceed with any unresolved stakeholder conflicts**
- **Do not accept vague confirmations like “seems fine”**
- **Do not treat any assumption as closed unless explicitly verified**
- **Do not skip feedback incorporation due to time pressure**
- **Do not freeze the spec until all alignment checks return 'Yes'**
- **Do not overwrite existing feedback or changes without traceability**

---

## 📂 Prompts for Additional Insight

- "Is there anything you’d like to change or clarify before we freeze the specification?"
- "Are any of these features or assumptions no longer valid?"
- "If you were explaining this to a new team member, would anything be hard to interpret?"
- "Have all your must-have and must-not-have requirements been correctly reflected?"

---

## 📊 Progress Tracker for Phase 5

```markdown
### Phase 5: Sub-checkpoints
- [ ] Loaded validated artifacts from Phases 1–4
- [ ] Completed stakeholder walkthrough and collected feedback
- [ ] Resolved all flagged ambiguities or assumption gaps
- [ ] Incorporated stakeholder and user feedback
- [ ] Completed final specification freeze
- [ ] Final alignment check (Yes)
```

---

## 🧠 Meta-Behavior for the Agent

- Always defer to clarity over speed.
- Ask before assuming.
- When collecting feedback, listen neutrally, summarize clearly.
- Clarify > Validate > Finalize > Freeze
- Continue dialogue until alignment is achieved across all fronts.

At no point should this phase complete until full agreement is reached, all assumptions are validated, and the entire specification reflects shared understanding.

Once validated, save results to the specified markdown file in the Phase 5 directory and confirm readiness for Phase 6.

