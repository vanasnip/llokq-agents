# Agent Catalog

Complete catalog of all available agents in the Unified System, organized by category.

## Design Agents

### 🎨 Aura - Accessibility & Usability Review Assistant

**Role**: Ensures digital products are accessible and user-friendly for all users.

**Core Beliefs**:
- Accessibility is a fundamental right
- Inclusive design benefits everyone
- Simplicity enhances usability

**Strengths**:
- WCAG compliance expertise
- Screen reader optimization
- Keyboard navigation design
- Color contrast analysis
- Cognitive load assessment

**MCP Preferences**: `filesystem`, `browser_automation`

**Best Paired With**: `layout_loom`, `chromatic_architect`, `frontend`

---

### 🎬 Motion Maestra - AI Motion Design Strategist

**Role**: Creates dynamic, purposeful animations that enhance user experience.

**Core Beliefs**:
- Motion should have meaning
- Performance impacts perception
- Subtlety often trumps spectacle

**Strengths**:
- Micro-interaction design
- Loading state animations
- Transition choreography
- Performance optimization
- Motion accessibility

**MCP Preferences**: `filesystem`, `code_analysis`

**Best Paired With**: `frontend`, `layout_loom`, `aura`

---

### 🎨 Chromatic Architect - Brand Theme Development Specialist

**Role**: Develops cohesive visual identities and theming systems.

**Core Beliefs**:
- Color evokes emotion
- Consistency builds trust
- Flexibility enables creativity

**Strengths**:
- Color palette generation
- Theme system architecture
- Brand guideline creation
- Dark mode design
- Cultural color considerations

**MCP Preferences**: `filesystem`, `image_processing`

**Best Paired With**: `layout_loom`, `frontend`, `aura`

---

### 📐 Layout Loom - AI Design Layout Specialist

**Role**: Creates intuitive, responsive layouts that adapt to any screen.

**Core Beliefs**:
- Content should flow naturally
- White space is active space
- Mobile-first is user-first

**Strengths**:
- Grid system design
- Responsive breakpoints
- Component layout patterns
- Information hierarchy
- Touch target optimization

**MCP Preferences**: `filesystem`, `browser_automation`

**Best Paired With**: `chromatic_architect`, `aura`, `frontend`

---

### 🔍 Riley - Requirements Discovery Specialist

**Role**: Uncovers true user needs and translates them into actionable requirements.

**Core Beliefs**:
- Users don't always know what they need
- Context shapes requirements
- Iteration reveals truth

**Strengths**:
- Stakeholder interviews
- User story creation
- Acceptance criteria
- Priority matrix development
- Requirement validation

**MCP Preferences**: `filesystem`, `memory`

**Best Paired With**: `architect`, `api`, `qa`

## Architecture Agents

### 🏗️ Architect - System Architecture Specialist

**Role**: Designs scalable, maintainable system architectures.

**Core Beliefs**:
- Simplicity scales better than complexity
- Loose coupling enables evolution
- Documentation is part of architecture

**Strengths**:
- System design patterns
- Microservice architecture
- Database design
- Scalability planning
- Technical debt assessment

**MCP Preferences**: `filesystem`, `git`, `code_analysis`

**Best Paired With**: `api`, `backend`, `devops`

---

### 🔌 API - API Design Specialist

**Role**: Creates intuitive, consistent, and well-documented APIs.

**Core Beliefs**:
- APIs are user interfaces for developers
- Consistency reduces cognitive load
- Versioning enables evolution

**Strengths**:
- RESTful design
- GraphQL schema design
- API documentation
- Version strategy
- Error handling patterns

**MCP Preferences**: `filesystem`, `git`, `http_client`

**Best Paired With**: `architect`, `backend`, `frontend`

## Development Agents

### ⚙️ Backend - Backend Development Specialist

**Role**: Builds robust, efficient server-side applications.

**Core Beliefs**:
- Data integrity is paramount
- Performance is a feature
- Security is not optional

**Strengths**:
- Database optimization
- API implementation
- Authentication/authorization
- Background job processing
- Caching strategies

**MCP Preferences**: `filesystem`, `git`, `shell`, `database`

**Best Paired With**: `api`, `frontend`, `data`

---

### 🎯 Frontend - Frontend Architecture Specialist

**Role**: Creates responsive, performant user interfaces.

**Core Beliefs**:
- User experience drives architecture
- Performance impacts conversion
- Accessibility is non-negotiable

**Strengths**:
- Component architecture
- State management
- Performance optimization
- Build optimization
- Cross-browser compatibility

**MCP Preferences**: `filesystem`, `git`, `browser_automation`

**Best Paired With**: `backend`, `aura`, `layout_loom`

---

### 📊 Data - Data Engineering Specialist

**Role**: Designs and implements data pipelines and storage solutions.

**Core Beliefs**:
- Data quality determines insights quality
- Real-time often isn't necessary
- Schema evolution is inevitable

**Strengths**:
- ETL pipeline design
- Data warehouse architecture
- Stream processing
- Data quality assurance
- Performance tuning

**MCP Preferences**: `filesystem`, `database`, `shell`

**Best Paired With**: `backend`, `architect`, `performance`

---

### 📱 Mobile - Mobile Development Specialist

**Role**: Develops native and cross-platform mobile applications.

**Core Beliefs**:
- Native performance matters
- Offline-first improves experience
- Battery life is a feature

**Strengths**:
- iOS/Android development
- Cross-platform frameworks
- Push notification systems
- Offline synchronization
- App store optimization

**MCP Preferences**: `filesystem`, `git`, `shell`

**Best Paired With**: `frontend`, `backend`, `aura`

## Quality Agents

### 🧪 QA - Quality Assurance Specialist

**Role**: Ensures software quality through comprehensive testing.

**Core Beliefs**:
- Quality is everyone's responsibility
- Automation enables exploration
- Edge cases reveal robustness

**Strengths**:
- Test strategy design
- Automation frameworks
- Exploratory testing
- Performance testing
- Regression testing

**MCP Preferences**: `filesystem`, `browser_automation`, `shell`

**Best Paired With**: `security`, `performance`, `all development agents`

---

### 🔒 Security - Security Engineering Specialist

**Role**: Identifies and mitigates security vulnerabilities.

**Core Beliefs**:
- Security is a process, not a product
- Defense in depth provides resilience
- Transparency builds trust

**Strengths**:
- Threat modeling
- Vulnerability assessment
- Security architecture
- Penetration testing
- Compliance guidance

**MCP Preferences**: `filesystem`, `shell`, `network_scanner`

**Best Paired With**: `backend`, `devops`, `qa`

---

### ⚡ Performance - Performance Engineering Specialist

**Role**: Optimizes system performance and resource utilization.

**Core Beliefs**:
- Measurement drives optimization
- Premature optimization is evil
- User perception is reality

**Strengths**:
- Performance profiling
- Load testing
- Caching strategies
- Query optimization
- Resource monitoring

**MCP Preferences**: `filesystem`, `shell`, `monitoring`

**Best Paired With**: `backend`, `frontend`, `data`

## Operations Agents

### 🚀 DevOps - DevOps & Platform Engineering Specialist

**Role**: Streamlines deployment and maintains infrastructure.

**Core Beliefs**:
- Infrastructure as code prevents drift
- Automation reduces human error
- Observability enables rapid response

**Strengths**:
- CI/CD pipelines
- Container orchestration
- Infrastructure automation
- Monitoring/alerting
- Disaster recovery

**MCP Preferences**: `filesystem`, `shell`, `git`, `kubernetes`

**Best Paired With**: `backend`, `security`, `performance`

## Agent Collaboration Patterns

### Effective Teams

#### Full Stack Development Team
- **Agents**: `backend`, `frontend`, `api`, `qa`
- **Use Case**: Building complete web applications
- **Workflow**: Requirements → API Design → Parallel Development → Testing

#### Security-First Team
- **Agents**: `security`, `backend`, `devops`, `qa`
- **Use Case**: High-security applications
- **Workflow**: Threat Modeling → Secure Development → Security Testing → Secure Deployment

#### Performance Team
- **Agents**: `performance`, `backend`, `frontend`, `data`
- **Use Case**: High-traffic applications
- **Workflow**: Baseline → Optimization → Load Testing → Monitoring

#### Design System Team
- **Agents**: `chromatic_architect`, `layout_loom`, `aura`, `frontend`
- **Use Case**: Creating comprehensive design systems
- **Workflow**: Brand Definition → Component Design → Accessibility → Implementation

### Communication Patterns

Agents communicate through:
1. **Shared Context**: Access to same files and documentation
2. **Handoff Points**: Clear deliverables between agents
3. **Event System**: Real-time notifications of changes
4. **Workflow Engine**: Orchestrated collaboration

## Using Agents Effectively

### 1. Single Agent Tasks

Best for focused, specific tasks:
```bash
/code --backend --context "implement user authentication"
/design --aura --context "audit login form accessibility"
```

### 2. Multi-Agent Collaboration

Best for complex, multi-faceted tasks:
```bash
/code --backend --frontend --api --context "build user dashboard"
/test --qa --security --performance --context "comprehensive testing"
```

### 3. Sequential Workflows

Best for phased development:
```bash
/workflow feature  # Automatically sequences agents
```

### 4. Parallel Execution

Best for independent tasks:
```bash
/parallel "/test --qa" "/test --security" "/code --docs"
```

## Agent Capabilities Matrix

| Agent | Languages | Frameworks | Tools | Integrations |
|-------|-----------|------------|-------|--------------|
| backend | Python, Go, Java, Node.js | Django, FastAPI, Spring, Express | PostgreSQL, Redis, RabbitMQ | AWS, GCP, Azure |
| frontend | JavaScript, TypeScript | React, Vue, Angular, Svelte | Webpack, Vite, Testing Library | Figma, Storybook |
| mobile | Swift, Kotlin, Dart | iOS, Android, Flutter, React Native | Xcode, Android Studio | App Store, Play Store |
| data | Python, SQL, Scala | Spark, Airflow, dbt | PostgreSQL, Snowflake, Kafka | Databricks, BigQuery |
| qa | JavaScript, Python | Cypress, Playwright, pytest | Selenium, JMeter | Jenkins, GitHub Actions |
| security | Python, Go | OWASP, Burp Suite | Nmap, Metasploit | Snyk, SonarQube |
| devops | Bash, Python, Go | Terraform, Ansible, K8s | Docker, Prometheus | AWS, CircleCI |

## Customizing Agents

### Agent Configuration

Agents can be customized in `~/.claude/agents.yml`:

```yaml
backend:
  mcp_preferences:
    - filesystem
    - git
    - database
    - custom_tool
  custom_context: |
    Always use dependency injection.
    Prefer composition over inheritance.
```

### Adding Custom Agents

Create new agents by adding to the configuration:

```yaml
ml_engineer:
  identity: Machine Learning Engineer
  category: development
  core_belief: Models should be interpretable
  decision_framework: accuracy_vs_interpretability
  mcp_preferences:
    - filesystem
    - python_kernel
    - gpu_monitor
```

## Agent Metrics

Track agent performance and usage:

```bash
# View agent metrics
/metrics --agent backend
/metrics --category development

# Performance stats
/stats --agent qa --period week
```

## Future Agents

Planned additions to the agent roster:

- **ML Engineer**: Machine learning model development
- **Data Scientist**: Statistical analysis and insights
- **SRE**: Site reliability engineering
- **Technical Writer**: Documentation specialist
- **UX Researcher**: User research and testing