# Deep Research Agent Architecture

This document explains the architecture and design patterns used in the OpenHands deep research agent implementation.

## Overview

The deep research agent demonstrates state-of-the-art patterns for building AI agents that can conduct comprehensive research on any topic. It combines multiple architectural patterns from leading frameworks while leveraging the OpenHands SDK's capabilities.

## Core Components

### 1. Task Decomposition (Planner Agent)

The planner breaks down complex research topics into manageable subtasks:

```python
class PlannerTool:
    - Decomposes research topics using LLM
    - Creates prioritized task lists
    - Manages task dependencies
    - Outputs structured ResearchPlan objects
```

**Key Features:**
- Supports different research depths (quick/moderate/deep)
- Generates 5-8 specific, actionable tasks
- Each task has priority and dependencies
- Uses Pydantic for type-safe data structures

### 2. Information Retrieval (Search Tool)

Web search capabilities using Tavily API:

```python
class SearchTool:
    - Performs targeted web searches
    - Returns structured results
    - Supports basic and advanced search depths
    - Handles errors gracefully
```

**Key Features:**
- Direct API integration (no MCP overhead)
- Structured SearchResult objects
- Relevance scoring
- Configurable result limits

### 3. Knowledge Synthesis (Synthesizer Agent)

Combines findings into coherent reports:

```python
class SynthesizerTool:
    - Aggregates research findings
    - Creates executive summaries
    - Maintains citation chains
    - Outputs markdown or JSON reports
```

**Key Features:**
- LLM-powered synthesis
- Structured ResearchReport objects
- Evidence-based findings with confidence scores
- Multiple output formats

### 4. Orchestration Layer

The ResearchOrchestrator manages the workflow:

```python
class ResearchOrchestrator:
    - Coordinates agent activities
    - Manages conversation flow
    - Tracks research state
    - Collects performance metrics
```

**Workflow Phases:**
1. **Planning**: Decompose topic into tasks
2. **Execution**: Search and gather information
3. **Synthesis**: Combine findings into report

## Data Models (Pydantic)

All data structures use Pydantic for validation:

```python
ResearchTask      # Individual research subtask
ResearchPlan      # Complete plan with tasks
SearchResult      # Web search result
ResearchFinding   # Synthesized insight
ResearchReport    # Final research output
```

## Design Patterns

### 1. Tool Factory Pattern

Tools are created using factory functions that receive conversation state:

```python
def create_research_tools(conv_state) -> List[ToolDefinition]:
    # Create tools with access to workspace and state
    return [PlannerTool.create(...), SearchTool.create(...), ...]
```

### 2. Action-Observation Pattern

Each tool follows the OpenHands pattern:
- **Action**: Typed input parameters
- **Observation**: Structured output with `to_llm_content()` method
- **Executor**: Implementation logic

### 3. Structured Output Pattern

All outputs use Pydantic models:
- Type safety and validation
- Clear data contracts
- Easy serialization
- Self-documenting

### 4. Phased Execution Pattern

Research follows clear phases:
- Each phase has specific objectives
- State persists between phases
- Progress tracking throughout

## Extension Points

### Adding New Tools

1. Define Action and Observation classes
2. Implement ToolExecutor
3. Create ToolDefinition
4. Register with factory function

### Custom Research Domains

1. Extend ResearchTask with domain-specific fields
2. Add specialized search strategies
3. Implement domain-specific synthesis rules

### Alternative Data Sources

1. Replace SearchTool with other APIs
2. Add database connectors
3. Integrate with knowledge graphs

## Performance Considerations

- **Token Usage**: Structured prompts minimize token consumption
- **API Calls**: Batch operations where possible
- **Error Handling**: Graceful degradation with fallbacks
- **Caching**: Consider caching search results (not implemented)

## Security Considerations

- **API Keys**: Use environment variables
- **Input Validation**: Pydantic validates all inputs
- **Output Sanitization**: Be careful with generated markdown
- **Rate Limiting**: Respect API limits

## Future Enhancements

1. **Sub-agent Delegation**: Spawn specialized research agents
2. **State Persistence**: Save/resume research sessions
3. **Iterative Refinement**: Multi-round research with feedback
4. **Parallel Execution**: Concurrent task processing
5. **Knowledge Graph**: Build connections between findings

## Comparison with Other Approaches

| Feature | Our Implementation | LangChain | Pydantic AI | Agno |
|---------|-------------------|-----------|-------------|------|
| Task Decomposition | LLM-based planner | Built-in planning | Manual workflows | Role-based |
| State Management | In-memory + files | Virtual filesystem | Schema + DB | Storage drivers |
| Tool Integration | Custom + built-in | Extensive tools | Function tools | MCP/DB/APIs |
| Structured Output | Pydantic models | File artifacts | Pydantic native | DB-backed |
| Orchestration | Phased workflow | Chain/Graph | App logic | Runtime managed |

## Best Practices

1. **Clear Prompts**: Use structured prompts for consistent results
2. **Error Handling**: Always provide fallbacks for tool failures
3. **Type Safety**: Leverage Pydantic for all data structures
4. **Modularity**: Keep tools focused on single responsibilities
5. **Observability**: Log key decisions and metrics

## Conclusion

This architecture provides a solid foundation for building sophisticated research agents. The modular design allows for easy extension while maintaining clean separation of concerns. The use of structured data throughout ensures reliability and makes the system easier to debug and maintain.