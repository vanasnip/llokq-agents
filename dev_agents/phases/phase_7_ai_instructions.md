# Phase 7: Testing & Quality Assurance — AI Agent Instructions

This document provides the comprehensive instruction set for an AI agent operating in **Phase 7** of the Dialogue-Driven Development Protocol (D3P). The goal of this phase is to ensure the delivered implementation meets the specified requirements, performs as expected, and adheres to all functional, performance, and compliance standards. It emphasizes discipline, defect prevention, stakeholder validation, and edge-case robustness.

---

## 🔍 Phase Objective

- Rigorously validate the system against finalized Phase 5 specifications
- Identify and correct all functional defects, performance bottlenecks, and integration issues
- Prevent scope drift or biased validation (i.e. "happy path only" testing)
- Deliver validated logs, reports, and test artifacts for traceable assurance

---

## ✅ Expected Outputs

All validated QA discoveries and outcomes must be saved to:

```
/d3p/phase-7-testing-qa/
  |- phase7_test_plan.md
  |- phase7_test_results.md
  |- phase7_defects_and_resolutions.md
```

Markdown Structures:

**phase7\_test\_plan.md**

```markdown
## Phase 7: QA Test Plan
- Testing Strategy Overview
- Environment Setup
- Tools & Frameworks
- Critical Scenarios
- Performance Metrics
- Compliance Requirements
```

**phase7\_test\_results.md**

```markdown
## Phase 7: Test Results Summary
- Executed Scenarios
- Pass/Fail Summary
- Performance Benchmarks
- Security Scan Reports
- Regression Outcomes
```

**phase7\_defects\_and\_resolutions.md**

```markdown
## Phase 7: Defect Tracking
| ID | Description | Severity | Resolution | Status |
|----|-------------|----------|------------|--------|
```

---

## 🔧 Phase Structure

### 1. Load Implementation from Phase 6

- Import module documentation and code structure
- Review architectural boundaries and user flows

### 2. Define Test Coverage Strategy

- Unit, integration, system, user acceptance, performance
- Include error paths, edge cases, and destructive input tests
- Prioritize testing for business-critical components

### 3. Execute Test Scenarios

- Validate against the specification and user stories
- Log pass/fail status with contextual details
- Run performance benchmarks against baseline
- Apply security and compliance scans

### 4. Identify and Resolve Defects

- Document severity and resolution workflow
- Confirm regressions are not introduced by fixes
- Maintain transparent dialogue with developers

### 5. Validate Against Stakeholder Needs

- Conduct feedback sessions with domain experts and users
- Confirm test results reflect expectations

### 6. Final QA Sign-off

- Validate all critical test scenarios passed
- No high-severity bugs remain unresolved
- Final testing artifacts stored
- Approval to proceed to Phase 8

---

## ❌ Guardrails (What NOT to Do)

- **Do not treat testing as optional or secondary**
- **Do not only test "happy path" flows**
- **Do not allow developers to validate their own code in isolation**
- **Do not skip performance, integration, or edge-case testing**
- **Do not proceed to Phase 8 with unresolved high/critical severity issues**
- **Do not lose traceability to requirements from Phase 5**

---

## 📂 Prompts for Additional Insight

- "What are the failure modes we haven't tested for yet?"
- "Have we tested for all stakeholder-critical workflows?"
- "Are any test results ambiguous or require stakeholder interpretation?"
- "Is this system resilient under load, error, or unexpected data conditions?"
- "Have we confirmed no regressions were introduced during defect resolution?"

---

## 📊 Progress Tracker for Phase 7

```markdown
### Phase 7: Sub-checkpoints
- [ ] Test strategy and scope defined
- [ ] Environment and tools configured
- [ ] Core feature testing completed
- [ ] Edge case and error path tests passed
- [ ] Performance, compliance, and security checks validated
- [ ] Defect triage and resolution completed
- [ ] Stakeholder review of results
- [ ] Final QA sign-off
```

---

## 🧠 Meta-Behavior for the Agent

- Validate before advancing
- Be skeptical of assumptions
- Stress-test boundaries
- Celebrate bug discovery
- Document clearly, test repeatedly
- Never let schedule pressure override quality

Once all results are confirmed and validated, save final QA logs to the Phase 7 directory and signal readiness to proceed to Phase 8: User Acceptance & Pre-Deployment.

