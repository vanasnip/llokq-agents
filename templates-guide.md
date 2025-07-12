# Templates & Examples Guide

> Ready-to-use templates for common workflows and agent outputs

## 📋 Template Categories

1. **Agent Activation Templates** - Quick agent switching
2. **Output Templates** - Consistent document formats
3. **Workflow Templates** - Common project patterns
4. **Handoff Templates** - Smooth transitions
5. **Learning Templates** - Knowledge capture

---

## 1. Agent Activation Templates

### Quick Agent Switch
```markdown
## 🎭 Activate {AGENT_NAME}

I need you to become the {AGENT_NAME} agent for this project.

**Your Identity**: {CORE_IDENTITY}
**Your Belief**: {CORE_BELIEF}
**Current Task**: {SPECIFIC_TASK}

Please approach this task from your unique perspective as {AGENT_NAME}.
```

### Batch Mode Activation
```markdown
## 🎭 Multi-Agent Batch Session

I need to work through multiple agents efficiently. Please maintain each agent's personality but work through them sequentially:

### Session Plan
1. **Riley** (30 min): Gather requirements for user authentication feature
2. **Aria** (30 min): Design REST API for auth endpoints
3. **Blake** (90 min): Implement auth service with JWT
4. **Quinn** (30 min): Create test plan for auth flow

### Rules
- Maintain each agent's unique perspective
- Build on previous agent's work
- Mark transitions clearly with "=== {AGENT} Complete ==="
- Keep all outputs in this conversation
```

### Agent Identity Reinforcement
```markdown
## Identity Check - {AGENT_NAME}

Before proceeding, let's reinforce your identity:

- I am {AGENT_NAME}, the {ROLE}
- My core belief: "{CORE_BELIEF}"
- I approach problems by: {PROBLEM_SOLVING_APPROACH}
- My success is measured by: {SUCCESS_METRICS}
- I always: {ALWAYS_DO}
- I never: {NEVER_DO}

Now, let's continue with the task at hand.
```

---

## 2. Output Templates

### Requirements Document (Riley)
```markdown
# Feature Requirements: {FEATURE_NAME}

## Overview
{ONE_PARAGRAPH_DESCRIPTION}

## User Stories
### Story 1: {TITLE}
**As a** {USER_TYPE}  
**I want to** {ACTION}  
**So that** {BENEFIT}

**Acceptance Criteria:**
- [ ] {CRITERION_1}
- [ ] {CRITERION_2}
- [ ] {CRITERION_3}

### Story 2: {TITLE}
{REPEAT_PATTERN}

## Technical Requirements
### Functional Requirements
- FR1: The system SHALL {REQUIREMENT}
- FR2: The system SHALL {REQUIREMENT}

### Non-Functional Requirements
- NFR1: Response time SHALL be < {TIME}ms
- NFR2: System SHALL handle {NUMBER} concurrent users

## Constraints
- {CONSTRAINT_1}
- {CONSTRAINT_2}

## Assumptions
- {ASSUMPTION_1}
- {ASSUMPTION_2}

## Edge Cases
1. **Scenario**: {DESCRIPTION}
   **Handling**: {HOW_TO_HANDLE}

2. **Scenario**: {DESCRIPTION}
   **Handling**: {HOW_TO_HANDLE}

## Open Questions
- [ ] {QUESTION_1}
- [ ] {QUESTION_2}

## Success Metrics
- {METRIC_1}: {CURRENT} → {TARGET}
- {METRIC_2}: {CURRENT} → {TARGET}
```

### API Specification (Aria)
```yaml
# API Specification: {API_NAME}

openapi: 3.0.0
info:
  title: {API_TITLE}
  version: 1.0.0
  description: {API_DESCRIPTION}

servers:
  - url: https://api.example.com/v1
    description: Production server
  - url: https://staging-api.example.com/v1
    description: Staging server

paths:
  /resources:
    get:
      summary: List all resources
      operationId: listResources
      tags:
        - Resources
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
            maximum: 100
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/Resource'
                  pagination:
                    $ref: '#/components/schemas/Pagination'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'

    post:
      summary: Create a new resource
      operationId: createResource
      tags:
        - Resources
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ResourceInput'
      responses:
        '201':
          description: Resource created
          headers:
            Location:
              schema:
                type: string
              description: URL of created resource
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Resource'

components:
  schemas:
    Resource:
      type: object
      required:
        - id
        - name
        - created_at
      properties:
        id:
          type: string
          format: uuid
        name:
          type: string
          minLength: 1
          maxLength: 255
        description:
          type: string
        created_at:
          type: string
          format: date-time
        updated_at:
          type: string
          format: date-time

    ResourceInput:
      type: object
      required:
        - name
      properties:
        name:
          type: string
          minLength: 1
          maxLength: 255
        description:
          type: string

    Pagination:
      type: object
      properties:
        page:
          type: integer
        limit:
          type: integer
        total:
          type: integer
        pages:
          type: integer

    Error:
      type: object
      required:
        - code
        - message
      properties:
        code:
          type: string
        message:
          type: string
        details:
          type: object

  responses:
    BadRequest:
      description: Bad request
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    
    Unauthorized:
      description: Unauthorized
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - bearerAuth: []
```

### Test Plan (Quinn)
```markdown
# Test Plan: {FEATURE_NAME}

## Test Overview
**Objective**: Ensure {FEATURE_NAME} meets all requirements and quality standards  
**Scope**: {WHAT_IS_INCLUDED}  
**Out of Scope**: {WHAT_IS_EXCLUDED}

## Test Strategy
### Test Levels
- **Unit Testing**: Individual component validation
- **Integration Testing**: Component interaction verification
- **System Testing**: End-to-end functionality
- **Acceptance Testing**: User requirement validation

### Test Types
- ✅ Functional Testing
- ✅ Performance Testing
- ✅ Security Testing
- ✅ Usability Testing
- ✅ Compatibility Testing

## Test Scenarios

### Scenario 1: {SCENARIO_NAME}
**Description**: {WHAT_IS_BEING_TESTED}  
**Priority**: High/Medium/Low  
**Test Data**: {REQUIRED_DATA}

#### Test Cases
**TC-001**: {TEST_CASE_NAME}
- **Preconditions**: {SETUP_REQUIRED}
- **Steps**:
  1. {STEP_1}
  2. {STEP_2}
  3. {STEP_3}
- **Expected Result**: {EXPECTED_OUTCOME}
- **Actual Result**: [To be filled during execution]
- **Status**: [Pass/Fail]

**TC-002**: {TEST_CASE_NAME}
{REPEAT_PATTERN}

### Scenario 2: {SCENARIO_NAME}
{REPEAT_PATTERN}

## Edge Cases
1. **Empty Input**: {HOW_TO_TEST}
2. **Maximum Values**: {HOW_TO_TEST}
3. **Special Characters**: {HOW_TO_TEST}
4. **Concurrent Access**: {HOW_TO_TEST}

## Performance Criteria
- Response Time: < {TIME}ms for 95th percentile
- Throughput: > {NUMBER} requests/second
- Resource Usage: < {PERCENTAGE}% CPU, < {SIZE}MB memory

## Test Environment
- **Server**: {SPECS}
- **Database**: {TYPE_AND_VERSION}
- **Browser**: {BROWSERS_TO_TEST}
- **Mobile**: {DEVICES_TO_TEST}

## Test Data Requirements
- {DATA_SET_1}
- {DATA_SET_2}
- {DATA_SET_3}

## Risk Assessment
| Risk | Impact | Mitigation |
|------|--------|------------|
| {RISK_1} | High | {MITIGATION_1} |
| {RISK_2} | Medium | {MITIGATION_2} |

## Exit Criteria
- [ ] All test cases executed
- [ ] No critical/high severity bugs
- [ ] Performance targets met
- [ ] Security scan passed
- [ ] Test coverage > 80%
```

### Backend Implementation (Blake)
```python
# Service Implementation Template
# {SERVICE_NAME} - {DESCRIPTION}

from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from dataclasses import dataclass

# Configure logging
logger = logging.getLogger(__name__)

# Data Models
@dataclass
class {ModelName}:
    """
    Represents a {model_description}
    
    Attributes:
        id: Unique identifier
        name: Display name
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    id: str
    name: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Service Layer
class {ServiceName}Service:
    """
    Business logic for {service_description}
    """
    
    def __init__(self, repository):
        self.repository = repository
        logger.info(f"{self.__class__.__name__} initialized")
    
    async def create_{resource}(self, data: Dict[str, Any]) -> {ModelName}:
        """
        Create a new {resource}
        
        Args:
            data: Resource data
            
        Returns:
            Created resource
            
        Raises:
            ValidationError: If data is invalid
            DatabaseError: If creation fails
        """
        try:
            # Validate input
            self._validate_create_data(data)
            
            # Create resource
            resource = await self.repository.create(data)
            
            logger.info(f"Created {resource.id}")
            return resource
            
        except Exception as e:
            logger.error(f"Failed to create resource: {str(e)}")
            raise
    
    async def get_{resource}(self, resource_id: str) -> Optional[{ModelName}]:
        """
        Retrieve a {resource} by ID
        
        Args:
            resource_id: Resource identifier
            
        Returns:
            Resource if found, None otherwise
        """
        return await self.repository.get(resource_id)
    
    async def list_{resources}(
        self, 
        page: int = 1, 
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        List {resources} with pagination
        
        Args:
            page: Page number (1-based)
            limit: Items per page
            filters: Optional filters
            
        Returns:
            Paginated response with items and metadata
        """
        offset = (page - 1) * limit
        
        items = await self.repository.list(
            offset=offset,
            limit=limit,
            filters=filters
        )
        
        total = await self.repository.count(filters)
        
        return {
            'data': [item.to_dict() for item in items],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        }
    
    def _validate_create_data(self, data: Dict[str, Any]) -> None:
        """Validate creation data"""
        required_fields = ['name']
        
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        if not data['name'].strip():
            raise ValueError("Name cannot be empty")

# API Endpoints
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/{resources}", tags=["{resources}"])

class Create{Resource}Request(BaseModel):
    name: str
    description: Optional[str] = None

class {Resource}Response(BaseModel):
    id: str
    name: str
    created_at: datetime
    updated_at: Optional[datetime]

@router.post("/", response_model={Resource}Response, status_code=201)
async def create_{resource}(request: Create{Resource}Request):
    """Create a new {resource}"""
    try:
        service = get_{resource}_service()  # Dependency injection
        resource = await service.create_{resource}(request.dict())
        return resource
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{resource_id}", response_model={Resource}Response)
async def get_{resource}(resource_id: str):
    """Get a {resource} by ID"""
    service = get_{resource}_service()
    resource = await service.get_{resource}(resource_id)
    
    if not resource:
        raise HTTPException(status_code=404, detail="{Resource} not found")
    
    return resource

@router.get("/", response_model=Dict[str, Any])
async def list_{resources}(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """List {resources} with pagination"""
    service = get_{resource}_service()
    return await service.list_{resources}(page=page, limit=limit)

# Tests
import pytest
from unittest.mock import Mock, AsyncMock

@pytest.fixture
def mock_repository():
    """Mock repository for testing"""
    return Mock()

@pytest.fixture
def service(mock_repository):
    """Service instance for testing"""
    return {ServiceName}Service(mock_repository)

@pytest.mark.asyncio
async def test_create_{resource}_success(service, mock_repository):
    """Test successful resource creation"""
    # Arrange
    test_data = {'name': 'Test Resource'}
    expected_resource = {ModelName}(
        id='123',
        name='Test Resource',
        created_at=datetime.utcnow()
    )
    mock_repository.create = AsyncMock(return_value=expected_resource)
    
    # Act
    result = await service.create_{resource}(test_data)
    
    # Assert
    assert result.id == '123'
    assert result.name == 'Test Resource'
    mock_repository.create.assert_called_once_with(test_data)

@pytest.mark.asyncio
async def test_create_{resource}_invalid_data(service):
    """Test creation with invalid data"""
    # Arrange
    test_data = {'name': ''}  # Empty name
    
    # Act & Assert
    with pytest.raises(ValueError, match="Name cannot be empty"):
        await service.create_{resource}(test_data)

# More tests...
```

---

## 3. Workflow Templates

### SaaS API CRUD Workflow
```yaml
# workflow-saas-crud.yaml
name: "SaaS CRUD API Development"
description: "Standard workflow for CRUD API endpoints"
type: "sequential"
estimated_duration: "4-6 hours"

phases:
  - phase: 1
    name: "Requirements & Data Model"
    duration: "45 minutes"
    agents:
      primary:
        - agent: "requirement_agent"
          role: "Define CRUD requirements and data model"
    activities:
      - "Define resource attributes"
      - "Specify validation rules"
      - "Document access control requirements"
      - "Define search/filter capabilities"
    outputs:
      - name: "crud_requirements.md"
        description: "CRUD operation specifications"
      - name: "data_model.md"
        description: "Resource data model"

  - phase: 2
    name: "API Design"
    duration: "45 minutes"
    agents:
      primary:
        - agent: "api_architect"
          role: "Design RESTful API"
    activities:
      - "Design REST endpoints"
      - "Define request/response schemas"
      - "Specify error responses"
      - "Document rate limiting"
    outputs:
      - name: "api_spec.yaml"
        description: "OpenAPI specification"

  - phase: 3
    name: "Implementation"
    duration: "2 hours"
    agents:
      primary:
        - agent: "backend_engineer"
          role: "Implement API and database"
    activities:
      - "Create database migrations"
      - "Implement service layer"
      - "Build API endpoints"
      - "Add validation and error handling"
    outputs:
      - name: "implementation/"
        description: "Service and API code"
      - name: "migrations/"
        description: "Database migrations"

  - phase: 4
    name: "Testing"
    duration: "1 hour"
    agents:
      primary:
        - agent: "qa_engineer"
          role: "Test all CRUD operations"
    activities:
      - "Write unit tests"
      - "Create integration tests"
      - "Test error scenarios"
      - "Validate performance"
    outputs:
      - name: "tests/"
        description: "Test suite"
      - name: "test_report.md"
        description: "Test results"
```

### Mobile Offline Sync Workflow
```yaml
# workflow-mobile-offline.yaml
name: "Mobile Offline Sync Feature"
description: "Workflow for implementing offline-capable mobile features"
type: "sequential_with_parallel"
estimated_duration: "2-3 days"

phases:
  - phase: 1
    name: "Sync Requirements"
    duration: "1 hour"
    agents:
      primary:
        - agent: "requirement_agent"
          role: "Define sync behavior and conflicts"
      supporting:
        - agent: "mobile_engineer"
          role: "Mobile-specific requirements"
    activities:
      - "Define offline scenarios"
      - "Specify conflict resolution"
      - "Document sync triggers"
      - "Define data priority"
    outputs:
      - name: "sync_requirements.md"
        description: "Offline sync specifications"

  - phase: 2
    name: "Architecture Design"
    duration: "1.5 hours"
    agents:
      primary:
        - agent: "system_architect"
          role: "Design sync architecture"
        - agent: "api_architect"
          role: "Design sync API"
    parallel: true
    activities:
      - "Design local storage schema"
      - "Create sync protocol"
      - "Design conflict resolution"
      - "Plan queue management"
    outputs:
      - name: "sync_architecture.md"
        description: "Sync system design"
      - name: "sync_api.yaml"
        description: "Sync API specification"

  - phase: 3
    name: "Implementation"
    duration: "6 hours"
    agents:
      primary:
        - agent: "mobile_engineer"
          role: "Mobile implementation"
        - agent: "backend_engineer"
          role: "Backend sync service"
    parallel: true
    activities:
      - "Implement local storage"
      - "Build sync engine"
      - "Create conflict resolution"
      - "Implement sync API"
    outputs:
      - name: "mobile_sync/"
        description: "Mobile sync implementation"
      - name: "backend_sync/"
        description: "Backend sync service"

  - phase: 4
    name: "Testing & Validation"
    duration: "2 hours"
    agents:
      primary:
        - agent: "qa_engineer"
          role: "Test sync scenarios"
      supporting:
        - agent: "mobile_engineer"
          role: "Device-specific testing"
    activities:
      - "Test offline operations"
      - "Test sync scenarios"
      - "Test conflict resolution"
      - "Test edge cases"
    outputs:
      - name: "sync_test_plan.md"
        description: "Comprehensive test scenarios"
      - name: "test_results.md"
        description: "Test execution results"
```

### Microservice Template
```yaml
# workflow-microservice.yaml
name: "Microservice Development"
description: "Complete microservice from scratch"
type: "sequential"
estimated_duration: "2 days"

phases:
  - phase: 1
    name: "Service Design"
    duration: "2 hours"
    agents:
      primary:
        - agent: "system_architect"
          role: "Design service boundaries"
      supporting:
        - agent: "api_architect"
          role: "Inter-service communication"
    activities:
      - "Define service responsibilities"
      - "Design service API"
      - "Plan data ownership"
      - "Design communication patterns"
    outputs:
      - name: "service_design.md"
        description: "Service architecture"
      - name: "api_contracts.yaml"
        description: "Service API contracts"

  # ... more phases ...
```

---

## 4. Handoff Templates

### Standard Handoff
```markdown
# Handoff: {FROM_AGENT} → {TO_AGENT}

**Date**: {TIMESTAMP}  
**Phase**: {PHASE_NUMBER} - {PHASE_NAME}  
**Status**: Phase {PREVIOUS_PHASE} Complete ✅

## Completed Work
{SUMMARY_OF_WHAT_WAS_ACCOMPLISHED}

### Deliverables
- ✅ {OUTPUT_1}: {BRIEF_DESCRIPTION}
- ✅ {OUTPUT_2}: {BRIEF_DESCRIPTION}
- ✅ {OUTPUT_3}: {BRIEF_DESCRIPTION}

### Key Decisions Made
1. **{DECISION_TOPIC}**: {WHAT_WAS_DECIDED}
   - Rationale: {WHY_THIS_DECISION}
   - Impact: {WHAT_THIS_MEANS}

2. **{DECISION_TOPIC}**: {WHAT_WAS_DECIDED}
   - Rationale: {WHY_THIS_DECISION}
   - Impact: {WHAT_THIS_MEANS}

## Context for {TO_AGENT}

### What You Need to Know
- {CRITICAL_CONTEXT_1}
- {CRITICAL_CONTEXT_2}
- {CRITICAL_CONTEXT_3}

### Your Mission
{CLEAR_DESCRIPTION_OF_WHAT_TO_AGENT_SHOULD_ACCOMPLISH}

### Starting Points
1. Review: `{FILE_TO_REVIEW}`
2. Reference: `{REFERENCE_DOCUMENT}`
3. Build upon: `{PREVIOUS_OUTPUT}`

### Constraints & Considerations
- {CONSTRAINT_1}
- {CONSTRAINT_2}
- {WATCH_OUT_FOR}

## Open Items
- [ ] {QUESTION_OR_TASK_1}
- [ ] {QUESTION_OR_TASK_2}

## Success Criteria
- [ ] {WHAT_DEFINES_SUCCESS_1}
- [ ] {WHAT_DEFINES_SUCCESS_2}
- [ ] {WHAT_DEFINES_SUCCESS_3}

---
*Ready for handoff. {TO_AGENT}, please confirm receipt and understanding.*
```

### Quick Handoff
```markdown
## ⚡ Quick Handoff: {FROM} → {TO}

**What's Done**: {ONE_LINE_SUMMARY}

**Key Output**: `{MAIN_FILE_PATH}`

**Your Task**: {WHAT_TO_DO_NEXT}

**Watch Out**: {ANY_WARNINGS}

*Go!*
```

### Blocked Handoff
```markdown
# 🚫 Blocked Handoff: {FROM_AGENT}

**Phase**: {PHASE} - {STATUS}  
**Blocker**: {WHAT_IS_BLOCKING}

## Work Completed So Far
- ✅ {COMPLETED_1}
- ✅ {COMPLETED_2}
- 🚫 {BLOCKED_ITEM}

## Blocker Details
**Issue**: {DETAILED_DESCRIPTION}  
**Impact**: {WHAT_THIS_BLOCKS}  
**Needed**: {WHAT_WOULD_UNBLOCK}

## Options
1. **Option A**: {WORKAROUND_1}
   - Pros: {PROS}
   - Cons: {CONS}

2. **Option B**: {WORKAROUND_2}
   - Pros: {PROS}
   - Cons: {CONS}

## Recommendation
{WHAT_YOU_RECOMMEND_DOING}

**Decision Needed From**: {WHO_CAN_DECIDE}
```

---

## 5. Learning Templates

### Pattern Discovery
```markdown
# Pattern: {PATTERN_NAME}

**Discovered Date**: {DATE}  
**Project**: {PROJECT_NAME}  
**Agent**: {WHO_DISCOVERED}  
**Category**: {API|Architecture|Code|Testing|Process}

## Pattern Description
{WHAT_IS_THIS_PATTERN}

## When to Use
- Context: {WHEN_THIS_APPLIES}
- Problem: {WHAT_PROBLEM_IT_SOLVES}
- Signals: {HOW_TO_RECOGNIZE_NEED}

## Implementation
```{language}
{CODE_EXAMPLE_OR_TEMPLATE}
```

## Example Usage
{CONCRETE_EXAMPLE_FROM_PROJECT}

## Benefits
- ⚡ {BENEFIT_1}
- 🎯 {BENEFIT_2}
- 📈 {BENEFIT_3}

## Trade-offs
- ⚠️ {CONSIDERATION_1}
- 💭 {CONSIDERATION_2}

## Related Patterns
- {RELATED_PATTERN_1}
- {RELATED_PATTERN_2}

## Tags
`{tag1}` `{tag2}` `{tag3}`
```

### Decision Record
```markdown
# Decision: {DECISION_TITLE}

**Date**: {DATE}  
**Agent**: {WHO_MADE_DECISION}  
**Status**: {Proposed|Accepted|Deprecated}

## Context
{WHAT_SITUATION_REQUIRED_A_DECISION}

## Decision
{WHAT_WAS_DECIDED}

## Considered Options
### Option 1: {OPTION_NAME}
- **Description**: {WHAT_THIS_OPTION_IS}
- **Pros**: 
  - {PRO_1}
  - {PRO_2}
- **Cons**:
  - {CON_1}
  - {CON_2}

### Option 2: {OPTION_NAME}
{SAME_STRUCTURE}

### Option 3: {OPTION_NAME}
{SAME_STRUCTURE}

## Rationale
{WHY_THE_CHOSEN_OPTION_WAS_SELECTED}

### Key Factors
1. {FACTOR_1}: {HOW_IT_INFLUENCED}
2. {FACTOR_2}: {HOW_IT_INFLUENCED}
3. {FACTOR_3}: {HOW_IT_INFLUENCED}

## Consequences
### Positive
- {GOOD_OUTCOME_1}
- {GOOD_OUTCOME_2}

### Negative
- {TRADE_OFF_1}
- {TRADE_OFF_2}

### Neutral
- {NEUTRAL_IMPACT_1}

## Implementation Notes
- {IMPLEMENTATION_DETAIL_1}
- {IMPLEMENTATION_DETAIL_2}

## Review Date
{WHEN_TO_REVISIT_THIS_DECISION}
```

### Retrospective
```markdown
# Project Retrospective: {PROJECT_NAME}

**Date**: {DATE}  
**Duration**: {START_DATE} to {END_DATE}  
**Team**: {AGENTS_INVOLVED}

## 📊 Project Metrics
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Duration | {TARGET} | {ACTUAL} | {✅/⚠️/❌} |
| Quality Score | {TARGET} | {ACTUAL} | {✅/⚠️/❌} |
| Test Coverage | {TARGET} | {ACTUAL} | {✅/⚠️/❌} |
| Bugs Found | {TARGET} | {ACTUAL} | {✅/⚠️/❌} |

## 📈 Agent Performance
| Agent | Time Spent | Quality | Efficiency | Notes |
|-------|------------|---------|------------|-------|
| Riley | {TIME} | {SCORE}/5 | {SCORE} | {NOTES} |
| Aria | {TIME} | {SCORE}/5 | {SCORE} | {NOTES} |
| Blake | {TIME} | {SCORE}/5 | {SCORE} | {NOTES} |
| Quinn | {TIME} | {SCORE}/5 | {SCORE} | {NOTES} |

## 🌟 What Went Well
### Process
- {SUCCESS_1}
- {SUCCESS_2}

### Technical
- {SUCCESS_1}
- {SUCCESS_2}

### Collaboration
- {SUCCESS_1}
- {SUCCESS_2}

## 🔧 What Needs Improvement
### Process Issues
- **Issue**: {WHAT_HAPPENED}
  - **Impact**: {IMPACT}
  - **Fix**: {PROPOSED_SOLUTION}

### Technical Challenges
- **Challenge**: {WHAT_WAS_DIFFICULT}
  - **Why**: {ROOT_CAUSE}
  - **Solution**: {HOW_TO_AVOID}

### Communication Gaps
- **Gap**: {WHAT_WAS_MISSED}
  - **Result**: {WHAT_HAPPENED}
  - **Prevention**: {HOW_TO_PREVENT}

## 💡 Key Learnings
1. **Learning**: {WHAT_WE_LEARNED}
   - **Application**: {HOW_TO_APPLY}

2. **Learning**: {WHAT_WE_LEARNED}
   - **Application**: {HOW_TO_APPLY}

3. **Learning**: {WHAT_WE_LEARNED}
   - **Application**: {HOW_TO_APPLY}

## 🎯 Action Items
- [ ] {ACTION_1} - Owner: {WHO} - Due: {WHEN}
- [ ] {ACTION_2} - Owner: {WHO} - Due: {WHEN}
- [ ] {ACTION_3} - Owner: {WHO} - Due: {WHEN}

## 📚 Patterns to Document
- {PATTERN_1}: {BRIEF_DESCRIPTION}
- {PATTERN_2}: {BRIEF_DESCRIPTION}

## 🚀 Recommendations for Next Project
### Do
- {RECOMMENDATION_1}
- {RECOMMENDATION_2}

### Don't
- {ANTI_PATTERN_1}
- {ANTI_PATTERN_2}

### Try
- {EXPERIMENT_1}
- {EXPERIMENT_2}
```

---

## 📝 Quick Reference Card

### Agent Activation Commands
```bash
# Single agent
switch-agent riley

# Batch mode (in prompt)
"Work through Riley → Aria → Blake → Quinn"

# Identity check (in prompt)
"Confirm your identity as {agent_name}"
```

### Phase Commands
```bash
# Start phase
phase start 1

# Complete phase
phase complete 1 requirements.md,user_stories.md

# Check status
phase status
```

### Quality Checks
```bash
# Validate outputs
validate phase 1

# Generate checklist
validate checklist requirements
```

### Common File Paths
```
/active_project/
  ├── artifacts/          # All outputs go here
  ├── handoffs/          # Handoff documents
  ├── context/           # Shared context
  ├── phase_status.md    # Current phase
  └── current_agent.md   # Active agent
```

---

## 🎨 Customization Guide

### Creating Custom Templates

1. **Identify Pattern**: What repeats across projects?
2. **Extract Structure**: What are the common elements?
3. **Add Variables**: Mark dynamic parts with {BRACKETS}
4. **Document Usage**: When and how to use it
5. **Test & Refine**: Use in real project, improve

### Template Best Practices

- **Clear Placeholders**: Use descriptive {VARIABLE_NAMES}
- **Include Examples**: Show filled-out versions
- **Explain Sections**: Add comments for clarity
- **Version Control**: Track template changes
- **Regular Updates**: Refine based on usage

---

*These templates are starting points. Customize them based on your specific needs and learnings!*