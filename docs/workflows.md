# Workflow Guide

Learn how to use pre-built workflows and create custom workflows for your development process.

## Overview

Workflows orchestrate multiple agents to accomplish complex tasks. They define:
- Which agents to use
- In what order
- What outputs to expect
- How to handle errors

## Pre-built Workflows

### Feature Development Workflow

Complete end-to-end feature development process.

```bash
/workflow feature
```

**Phases**:

1. **Requirements Discovery** (`riley`, `architect`)
   - Gather requirements
   - Define acceptance criteria
   - Create technical specifications

2. **Architecture Design** (`architect`, `api`)
   - System design
   - API specification
   - Database schema

3. **UI/UX Design** (`layout_loom`, `chromatic_architect`, `aura`)
   - Wireframes and mockups
   - Design system components
   - Accessibility review

4. **Implementation** (`backend`, `frontend`, `mobile`)
   - Parallel development
   - Code review
   - Integration

5. **Testing** (`qa`, `security`, `performance`)
   - Unit and integration tests
   - Security scanning
   - Performance benchmarks

6. **Deployment** (`devops`)
   - CI/CD pipeline
   - Staging deployment
   - Production release

**Example Output Structure**:
```
feature-workflow/
├── requirements/
│   ├── user-stories.md
│   ├── acceptance-criteria.md
│   └── technical-spec.md
├── architecture/
│   ├── system-design.md
│   ├── api-spec.yaml
│   └── database-schema.sql
├── design/
│   ├── wireframes/
│   ├── components/
│   └── accessibility-report.md
├── implementation/
│   ├── backend/
│   ├── frontend/
│   └── mobile/
├── testing/
│   ├── test-results.md
│   ├── security-scan.md
│   └── performance-report.md
└── deployment/
    ├── ci-cd-config.yml
    └── deployment-guide.md
```

### Bug Investigation Workflow

Systematic approach to finding and fixing bugs.

```bash
/workflow bug
```

**Phases**:

1. **Triage** (`qa`)
   - Reproduce issue
   - Categorize severity
   - Initial assessment

2. **Root Cause Analysis** (`backend`, `frontend`, `architect`)
   - Code investigation
   - System analysis
   - Identify root cause

3. **Fix Implementation** (`backend`, `frontend`)
   - Develop fix
   - Write tests
   - Code review

4. **Verification** (`qa`)
   - Test fix
   - Regression testing
   - Confirm resolution

5. **Deployment** (`devops`)
   - Deploy to staging
   - Monitor
   - Production release

**Workflow Commands**:
```bash
# Start bug workflow with context
/workflow bug --issue "Users can't login after password reset"

# Check status
/workflow --status

# Move to next phase
/workflow --next

# Skip to specific phase
/workflow --goto 3
```

### Security Audit Workflow

Comprehensive security assessment and remediation.

```bash
/workflow security
```

**Phases**:

1. **Threat Modeling** (`security`, `architect`)
   - Identify assets
   - Map attack vectors
   - Risk assessment

2. **Vulnerability Scanning** (`security`)
   - Automated scans
   - Manual testing
   - Code analysis

3. **Remediation Planning** (`security`, `backend`, `devops`)
   - Prioritize fixes
   - Design solutions
   - Implementation plan

4. **Implementation** (`backend`, `frontend`)
   - Apply security fixes
   - Update dependencies
   - Harden configuration

5. **Verification** (`security`, `qa`)
   - Retest vulnerabilities
   - Penetration testing
   - Compliance check

**Security Workflow Options**:
```bash
# Full audit
/workflow security --full

# Quick scan
/workflow security --quick

# Compliance focused
/workflow security --compliance OWASP
```

### Performance Optimization Workflow

Identify and resolve performance bottlenecks.

```bash
/workflow performance
```

**Phases**:

1. **Baseline** (`performance`)
   - Current metrics
   - User journeys
   - SLA definition

2. **Profiling** (`performance`, `backend`, `frontend`)
   - Code profiling
   - Database analysis
   - Network analysis

3. **Optimization** (`backend`, `frontend`, `data`)
   - Code optimization
   - Query tuning
   - Caching implementation

4. **Validation** (`performance`, `qa`)
   - Load testing
   - Benchmark comparison
   - User testing

## Custom Workflows

### Creating a Custom Workflow

Add to `~/.claude/workflows.yml`:

```yaml
custom_workflows:
  api_redesign:
    name: "API Redesign Workflow"
    description: "Redesign existing API for better performance"
    phases:
      - name: "Current State Analysis"
        agents: ["api", "performance"]
        outputs:
          - current-api-analysis.md
          - performance-baseline.md
      
      - name: "New Design"
        agents: ["api", "architect"]
        outputs:
          - new-api-spec.yaml
          - migration-plan.md
      
      - name: "Implementation"
        agents: ["backend"]
        outputs:
          - implementation/
      
      - name: "Testing"
        agents: ["qa", "performance"]
        outputs:
          - test-results.md
          - performance-comparison.md
```

### Workflow Definition Structure

```yaml
workflow_name:
  name: "Human Readable Name"
  description: "What this workflow accomplishes"
  
  # Optional: Required inputs
  inputs:
    - name: "project_name"
      type: "string"
      required: true
    - name: "target_environment"
      type: "string"
      default: "staging"
  
  # Workflow phases
  phases:
    - name: "Phase Name"
      agents: ["agent1", "agent2"]
      parallel: false  # Run agents in parallel
      
      # Optional: Phase-specific context
      context: |
        Additional context for agents in this phase
      
      # Expected outputs
      outputs:
        - path/to/output.md
        - another/output.yaml
      
      # Optional: Success criteria
      success_criteria:
        - "All tests pass"
        - "Performance within SLA"
      
      # Optional: Error handling
      on_error: "continue" # or "abort", "retry"
```

### Advanced Workflow Features

#### Conditional Phases

```yaml
phases:
  - name: "Security Scan"
    condition: "environment == 'production'"
    agents: ["security"]
    
  - name: "Quick Deploy"
    condition: "environment == 'development'"
    agents: ["devops"]
```

#### Dynamic Agent Selection

```yaml
phases:
  - name: "Platform Specific Build"
    agents: 
      select_by: "platform"
      options:
        web: ["frontend", "backend"]
        mobile: ["mobile", "backend"]
        desktop: ["desktop", "backend"]
```

#### Workflow Composition

```yaml
mega_workflow:
  name: "Complete Feature with Security"
  compose:
    - workflow: "feature"
      phases: [1, 2, 3, 4]  # Use specific phases
    - workflow: "security"
      phases: [1, 2]
    - workflow: "feature"
      phases: [5, 6]  # Continue with remaining phases
```

## Workflow Management

### Workflow State

Workflows maintain state between executions:

```bash
# Save workflow state
/workflow --save my-feature-v1

# Load workflow state
/workflow --load my-feature-v1

# List saved states
/workflow --list-saves
```

### Workflow History

```bash
# View workflow history
/workflow --history

# View specific run
/workflow --history abc123

# Export workflow run
/workflow --export abc123 --format json
```

### Workflow Monitoring

```bash
# Real-time monitoring
/workflow --monitor

# Show metrics
/workflow --metrics

# Performance analysis
/workflow --analyze performance
```

## Best Practices

### 1. Start with Pre-built Workflows

```bash
# Use as templates
/workflow feature --dry-run > my-workflow-plan.md

# Customize from there
/workflow feature --customize
```

### 2. Define Clear Outputs

Each phase should produce specific, verifiable outputs:

```yaml
outputs:
  - api-spec.yaml      # Structured data
  - README.md          # Documentation
  - test-results.json  # Test results
```

### 3. Use Parallel Execution

When tasks are independent:

```yaml
phases:
  - name: "Parallel Testing"
    agents: ["qa", "security", "performance"]
    parallel: true  # Run all agents simultaneously
```

### 4. Handle Errors Gracefully

```yaml
phases:
  - name: "Deployment"
    agents: ["devops"]
    on_error: "retry"
    retry_count: 3
    retry_delay: 60  # seconds
```

### 5. Version Your Workflows

```bash
# Version control workflows
cd ~/.claude
git init
git add workflows.yml
git commit -m "Add custom API workflow"
```

## Workflow Examples

### Example 1: Documentation Workflow

```yaml
documentation:
  name: "Documentation Update"
  phases:
    - name: "Analyze Code"
      agents: ["backend", "frontend"]
      outputs:
        - code-analysis.md
    
    - name: "Generate Docs"
      agents: ["api"]
      outputs:
        - api-docs/
    
    - name: "Review"
      agents: ["qa"]
      outputs:
        - review-comments.md
```

### Example 2: Refactoring Workflow

```yaml
refactoring:
  name: "Code Refactoring"
  phases:
    - name: "Impact Analysis"
      agents: ["architect", "backend"]
      outputs:
        - impact-analysis.md
        - refactoring-plan.md
    
    - name: "Refactor"
      agents: ["backend", "frontend"]
      parallel: true
      outputs:
        - refactored/
    
    - name: "Verify"
      agents: ["qa", "performance"]
      outputs:
        - verification-report.md
```

### Example 3: Release Workflow

```yaml
release:
  name: "Production Release"
  inputs:
    - name: "version"
      required: true
    - name: "changelog"
      required: true
  
  phases:
    - name: "Pre-flight Checks"
      agents: ["qa", "security", "performance"]
      parallel: true
      
    - name: "Build & Package"
      agents: ["devops"]
      
    - name: "Deploy to Staging"
      agents: ["devops"]
      
    - name: "Staging Validation"
      agents: ["qa"]
      
    - name: "Production Deploy"
      agents: ["devops"]
      condition: "staging_tests == 'passed'"
      
    - name: "Post-Deploy Monitoring"
      agents: ["devops", "performance"]
```

## Troubleshooting Workflows

### Common Issues

1. **Workflow Stuck**
   ```bash
   # Check status
   /workflow --status --verbose
   
   # Force next phase
   /workflow --force-next
   
   # Abort workflow
   /workflow --abort
   ```

2. **Missing Outputs**
   ```bash
   # Verify outputs
   /workflow --verify-outputs
   
   # Regenerate phase
   /workflow --retry-phase 3
   ```

3. **Agent Conflicts**
   ```bash
   # Check agent availability
   /agent --status
   
   # Reset agents
   /agent --reset
   ```

## Integration with CI/CD

### GitHub Actions

```yaml
name: Feature Workflow
on: 
  pull_request:
    types: [opened]

jobs:
  feature_workflow:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Run Feature Workflow
        run: |
          unified-agents workflow feature \
            --ci-mode \
            --output-dir ${{ github.workspace }}/workflow-output
      
      - name: Upload Artifacts
        uses: actions/upload-artifact@v2
        with:
          name: workflow-output
          path: workflow-output/
```

### GitLab CI

```yaml
feature_workflow:
  stage: development
  script:
    - unified-agents workflow feature --ci-mode
  artifacts:
    paths:
      - workflow-output/
    expire_in: 1 week
```

## Next Steps

1. Try the pre-built workflows with sample projects
2. Customize a workflow for your needs
3. Create team-specific workflows
4. Integrate with your CI/CD pipeline
5. Share workflows with your team