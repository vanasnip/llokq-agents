# Discourse Agent Usage Guide

The Discourse Agent facilitates structured conversations, capturing insights and decisions throughout the development process.

## Quick Start

### 1. Start a Discussion
```json
{
  "method": "tools/call",
  "params": {
    "name": "ua_discourse_discuss",
    "arguments": {
      "topic": "API Design for User Authentication",
      "context": {
        "project": "MyApp",
        "phase": "architecture"
      }
    }
  }
}
```

### 2. Add Questions
```json
{
  "method": "tools/call",
  "params": {
    "name": "ua_discourse_question",
    "arguments": {
      "question": "Should we use JWT or session-based authentication?",
      "category": "security"
    }
  }
}
```

### 3. Record Insights
```json
{
  "method": "tools/call",
  "params": {
    "name": "ua_discourse_insight",
    "arguments": {
      "insight": "JWT provides stateless auth but requires careful token management",
      "references": ["RFC 7519", "OWASP guidelines"]
    }
  }
}
```

### 4. Make Decisions
```json
{
  "method": "tools/call",
  "params": {
    "name": "ua_discourse_decide",
    "arguments": {
      "decision": "Use JWT with refresh token rotation for enhanced security",
      "context": {
        "factors": ["scalability", "security", "user experience"],
        "tradeoffs": "Increased complexity for better security"
      }
    }
  }
}
```

### 5. Summarize Progress
```json
{
  "method": "tools/call",
  "params": {
    "name": "ua_discourse_summarize",
    "arguments": {
      "depth": "detailed"
    }
  }
}
```

### 6. Archive Conversation
```json
{
  "method": "tools/call",
  "params": {
    "name": "ua_discourse_archive",
    "arguments": {
      "title": "Authentication Architecture Decision"
    }
  }
}
```

## Conversation Flow

The Discourse Agent guides conversations through natural phases:

1. **Exploration** - Setting context and asking questions
2. **Analysis** - Transitioning from questions to insights
3. **Synthesis** - Combining insights into understanding
4. **Decision** - Recording concrete decisions
5. **Archive** - Preserving the conversation

## Storage

Conversations are stored as JSON files in:
- `~/.mcp/conversations/discourse/`
- Each conversation includes all entries, metadata, and timestamps
- Files can be searched and retrieved later

## Integration with Other Agents

The Discourse Agent complements other agents by:
- Facilitating requirements discovery with the QA Agent
- Capturing architecture decisions with the System Architect
- Recording API design rationale with the Backend Agent

## Best Practices

1. **Start with Context**: Always begin with `discuss` to set the topic
2. **Ask Before Answering**: Use questions to explore the problem space
3. **Reference Sources**: Include references with insights for traceability
4. **Decide Explicitly**: Use the decide tool for clear decision records
5. **Archive Regularly**: Preserve important conversations for future reference