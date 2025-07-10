# Phase 9: Deployment & Go-Live — AI Agent Instructions

This document outlines the complete instruction set for an AI agent operating in **Phase 9** of the Dialogue-Driven Development Protocol (D3P). This phase represents the formal release of the system into production and is one of the most risk-sensitive moments in the lifecycle. The AI agent is expected to coordinate deployment execution, risk mitigation, and post-deployment readiness with discipline, alignment, and traceability.

All deployment activities, rollback plans, metrics tracking strategies, and go-live support setups must be saved in Markdown format under the directory:

```
/d3p/phase-9-deployment-golive/
```

---

## 🔍 Phase Objective

- Execute production release with minimal risk
- Monitor deployment success using live metrics and error signals
- Maintain readiness to rollback if required
- Coordinate communication, support coverage, and verification processes

---

## ✅ Expected Outputs

```
/d3p/phase-9-deployment-golive/
  |- phase9_deployment_plan.md
  |- phase9_go_live_monitoring.md
  |- phase9_post_deployment_verification.md
  |- phase9_roll_back_strategy.md
```

**Each file must clearly document:**

- Deployment steps, responsibilities, and timing
- Monitoring dashboards, success/failure signals, alert thresholds
- Verification checklist for each core service/module
- Defined criteria and procedures for rollback or hotfix

---

## 🔧 Phase Structure

### 1. Final Deployment Planning

- Confirm all Go conditions from Phase 8 are met
- Review final infrastructure configurations, user access, environment parity
- Lock-in release window and notify all affected parties

### 2. Execute Go-Live

- Coordinate deployment execution with engineering and ops
- Monitor real-time metrics (errors, performance, user activity)
- Use (Yes | No | Clarify) loop to validate live status and stakeholder confidence

### 3. Track Success Signals

- Define real-time health indicators:
  - Error logs
  - CPU/memory/network metrics
  - API latency
  - Business KPIs (e.g., logins, transactions)
- Set alert thresholds and check-in intervals

### 4. Verify Feature Availability and Data Integrity

- Confirm that user-facing functionality is behaving as expected
- Perform smoke testing on critical flows
- Check for any silent failures, broken configurations, or permission gaps

### 5. Coordinate Support and Communication

- Ensure users, business teams, and support staff are informed and ready
- Route feedback to live issue tracker if necessary
- Maintain open dialogue with all stakeholders during launch window

### 6. Execute Rollback if Criteria Met

- Monitor for signs of critical failure
- Have predefined authority tree for rollback decision
- Restore last-known-good configuration if required

---

## ❌ Guardrails (What NOT to Do)

- **Do not deploy without an immediate rollback plan in place**
- **Do not proceed during peak hours unless explicitly cleared**
- **Do not lose observability — monitoring must be active during and after deploy**
- **Do not treat deployment as “complete” immediately after push — verify live behavior first**
- **Do not delay stakeholder notifications or assume silent success**
- **Do not perform final deployment without documented Go decision from Phase 8**

---

## 📂 Prompts for Insight & Validation

- "What are the specific indicators that will confirm success or signal failure during deployment?"
- "Who is authorized to make the rollback decision, and are they present and reachable during deployment?"
- "How are we logging and tracking errors or performance changes in the first 2 hours post-launch?"
- "What systems or interfaces must be manually verified after deployment?"
- "Has every support channel been briefed and staffed for this release window?"

---

## 📊 Progress Tracker for Phase 9

```markdown
### Phase 9: Sub-checkpoints
- [ ] Final Go decision received and documented
- [ ] Deployment steps reviewed and approved by all parties
- [ ] Monitoring dashboards configured and validated
- [ ] Go-live executed and success signals actively tracked
- [ ] Smoke testing and feature validation completed
- [ ] Stakeholders updated with live status and any incidents
- [ ] Rollback plan confirmed or retired after stability achieved
```

---

## 🧠 Meta-Behavior for the Agent

- Coordinate > Assume
- Monitor > Hope
- Validate > Rush
- Communicate > Obscure
- Log Everything > Rely on Memory

> Once deployment is verified and post-launch stability confirmed, save all Phase 9 documentation to `/phase-9-deployment-golive/` and prompt transition to Phase 10: Operations & Continuous Improvement.

