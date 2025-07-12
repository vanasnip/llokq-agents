# Handoff Templates

## ⚡ Quick Handoff Template

```markdown
## ⚡ Quick Handoff: {FROM} → {TO}

**Date**: {TIMESTAMP}
**Phase**: {CURRENT_PHASE}

**What's Done**: {ONE_LINE_SUMMARY}

**Key Output**: `{MAIN_FILE_PATH}`

**Your Task**: {WHAT_TO_DO_NEXT}

**Important Context**: {KEY_DETAILS}

**Watch Out**: {ANY_WARNINGS_OR_EDGE_CASES}

*Ready for {TO} to take over!*
```

## 📋 Detailed Handoff Template

```markdown
# Handoff: {FROM_AGENT} → {TO_AGENT}

**Date**: {TIMESTAMP}  
**Phase**: {PHASE_NUMBER} - {PHASE_NAME}  
**Status**: Phase Complete ✅

## Completed Work

{SUMMARY_OF_WHAT_WAS_ACCOMPLISHED}

### Deliverables
- ✅ `{OUTPUT_1}`: {BRIEF_DESCRIPTION}
- ✅ `{OUTPUT_2}`: {BRIEF_DESCRIPTION}
- ✅ `{OUTPUT_3}`: {BRIEF_DESCRIPTION}

### Key Decisions Made
1. **{DECISION_TOPIC}**: {WHAT_WAS_DECIDED}
   - Rationale: {WHY_THIS_DECISION}

## For {TO_AGENT}

### Your Mission
{CLEAR_DESCRIPTION_OF_WHAT_NEXT_AGENT_SHOULD_ACCOMPLISH}

### Starting Points
1. Review: `{FILE_TO_REVIEW}`
2. Build upon: `{PREVIOUS_OUTPUT}`

### Critical Considerations
- {IMPORTANT_POINT_1}
- {IMPORTANT_POINT_2}

---
*{TO_AGENT}, please confirm receipt and begin your phase.*
```

## Example Quick Handoff

```markdown
## ⚡ Quick Handoff: Riley → Aria

**Date**: 2024-01-10 14:30
**Phase**: Requirements Complete

**What's Done**: Gathered requirements for user authentication API with email and OAuth support

**Key Output**: `/artifacts/requirements/auth_requirements.md`

**Your Task**: Design RESTful API endpoints for the authentication system

**Important Context**: Client wants JWT tokens with 24hr expiry, refresh token support required

**Watch Out**: Must support both mobile and web clients with different token strategies

*Ready for Aria to take over!*
```