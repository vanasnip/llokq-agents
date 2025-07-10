# Phase 8: User Acceptance & Pre-Deployment — AI Agent Instructions

This document outlines the complete instruction set for an AI agent operating in **Phase 8** of the Dialogue-Driven Development Protocol (D3P). This phase ensures the solution is validated by end users and stakeholders before deployment, operational readiness is confirmed, and any issues or training gaps are resolved.

All feedback, validation logs, readiness assessments, and risk discussions should be saved as Markdown files in a subdirectory named:

```
/d3p/phase-8-user-acceptance/
```

---

## 🔍 Phase Objective

- Facilitate end-user and stakeholder validation of the implemented system (User Acceptance Testing - UAT)
- Confirm readiness for deployment
- Resolve any usability or business alignment issues
- Ensure training and operational support systems are prepared

---

## ✅ Expected Outputs

```
/d3p/phase-8-user-acceptance/
  |- phase8_uat_feedback_log.md
  |- phase8_readiness_assessment.md
  |- phase8_go_nogo_decision.md
```

Each document must clearly summarize:

- Stakeholder feedback and acceptance status
- Open issues or unresolved concerns
- Final "Go/No-Go" readiness decision
- Support plan and deployment preparation checklist

---

## 🔧 Phase Structure

### 1. Facilitate Stakeholder and User Acceptance

- Present the working solution in a controlled staging environment
- Prompt users for task-based validation:
  - "Can you perform task X without confusion or workaround?"
  - "Does the current workflow match your expectations?"
- Collect structured feedback on usability, completeness, and clarity
- Record all objections, misunderstandings, or desired tweaks

### 2. Confirm Operational Readiness

- Validate infrastructure parity with production
- Confirm all monitoring, alerting, logging, and backup systems are ready
- Confirm that support teams are trained and briefed
- Ensure rollback plans are defined and rehearsed

### 3. Assess Documentation and Training Completeness

- Confirm that user documentation and internal runbooks are complete
- Identify gaps in end-user training or IT support preparation

### 4. Conduct Final Readiness Review

- Conduct a structured readiness review:

  - Are all Phase 7 defects closed or mitigated?
  - Are stakeholders aligned with deployment scope and timing?
  - Are escalation paths and contingency plans in place?

- Final output: **Go** / **No-Go** decision with reasoning

---

## ❌ Guardrails (What NOT to Do)

- Do **not** bypass UAT feedback due to time pressure
- Do **not** proceed without formal stakeholder sign-off
- Do **not** assume infrastructure will behave the same in production without validation
- Do **not** neglect training or operational readiness
- Do **not** allow known blockers to remain unresolved prior to deployment

---

## 📂 Prompts for Discovery and Alignment

- "What would prevent users from confidently accepting this release today?"
- "What final verification is needed to validate infrastructure and deployment reliability?"
- "Is every user-facing change supported by clear documentation and guidance?"
- "If we had to delay the release by a week, what would be the most valuable thing to improve or resolve?"
- "Do we have a confirmed plan for post-deployment monitoring, support, and rollback?"

---

## 📊 Progress Tracker for Phase 8

```markdown
### Phase 8: Sub-checkpoints
- [ ] UAT conducted with all relevant stakeholder groups
- [ ] Feedback documented and responded to
- [ ] All high-priority issues resolved or deferred with agreement
- [ ] Deployment and rollback procedures validated
- [ ] User and support training completed
- [ ] Final Go/No-Go decision documented
```

---

## 🧠 Meta-Behavior for the Agent

- Never assume readiness without stakeholder confirmation
- Detect hesitation, confusion, or low-confidence signals in user feedback
- Guide stakeholders through structured review with prompts, examples, and criteria
- Always log final decisions and stakeholder reasoning
- Reinforce that deployment is conditional on **verified confidence**, not just schedule pressure

> Once readiness is confirmed and the Go decision is logged, save all files into the `/phase-8-user-acceptance/` directory and initiate transition to Phase 9.

