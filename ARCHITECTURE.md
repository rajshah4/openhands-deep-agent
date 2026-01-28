# Deep Research Agent Architecture

This document explains the architecture and design patterns used in the OpenHands deep research agent implementation.

## Overview

The implementation demonstrates practical patterns for building AI research agents using the OpenHands SDK. It emphasizes simplicity, using file-based state management and multi-agent collaboration.

## Core Components

### 1. Custom Tool Pattern (Action → Observation → Executor → ToolDefinition)

The OpenHands SDK requires a specific pattern for custom tools:

```python
# 1. Action: Typed input (what the agent sends)
class SearchAction(Action):
    query: str = Field(description="Search query")

# 2. Observation: Typed output (what the agent receives)
class SearchObservation(Observation):
    results: str = Field(description="Results")
    @property
    def to_llm_content(self):
        return [TextContent(text=self.results)]

# 3. Executor: Implementation logic
class SearchExecutor(ToolExecutor):
    def __call__(self, action: SearchAction, conversation=None) -> SearchObservation:
        try:
            r = tavily.search(query=action.query, max_results=5)
            return SearchObservation(results=formatted_results)
        except Exception as e:
            # Return error as observation (don't raise!)
            return SearchObservation(results=f"Search failed: {e}")

# 4. ToolDefinition: Factory that creates tool instances
class SearchTool(ToolDefinition[SearchAction, SearchObservation]):
    @classmethod
    def create(cls, conv_state) -> List["SearchTool"]:
        return [cls(
            description="Web search via Tavily",
            action_type=SearchAction,
            observation_type=SearchObservation,
            executor=SearchExecutor()
        )]

# 5. Register the tool
register_tool("TavilySearch", SearchTool.create)
```

**Why this pattern?**
- **Type safety**: Pydantic validates inputs/outputs
- **Serialization**: Actions/Observations can be persisted
- **Factory pattern**: Tools can access conversation state during creation

### 2. Built-in Tools

The SDK provides ready-to-use tools:

```python
from openhands.tools.file_editor import FileEditorTool  # Read/write files
from openhands.tools.terminal import TerminalTool        # Run commands
from openhands.tools.task_tracker import TaskTrackerTool # Track tasks
```

### 3. Multi-Agent Collaboration

Two separate LLM instances work together:

```python
# Research agent (GPT-4o) - creates plans, executes searches
llm = LLM(model="openai/gpt-4o", api_key=...)
agent = Agent(llm=llm, tools=[FileEditorTool, TavilySearch])

# Critique agent (GPT-5.1) - evaluates plans, synthesizes reports
critique_llm = LLM(model="openai/gpt-5.1", api_key=...)
critique_agent = Agent(llm=critique_llm, tools=[FileEditorTool])
```

Each agent has its own `Conversation` and can read/write shared files.

### 4. File-Based State Management

State is managed through markdown files (human-readable, persistent):

| File | Purpose |
|------|---------|
| `research_plan.md` | Working document with sub-questions + raw findings |
| `critique.md` | Plan evaluation feedback from critique agent |
| `research_report.md` | Final synthesized report |

Agents read and write these files using `FileEditorTool`.

### 5. Native SDK Persistence

The SDK automatically saves conversation state:

```python
import uuid

SESSION_NAME = "my-research-session"
SESSION_ID = uuid.uuid5(uuid.NAMESPACE_DNS, SESSION_NAME)

conversation = Conversation(
    agent=agent,
    workspace=os.getcwd(),
    persistence_dir="./.conversations",  # Auto-save location
    conversation_id=SESSION_ID,           # Deterministic ID for resume
)
```

**How it works:**
- Every event (message, tool call, response) is saved
- Restart the conversation with same ID → resumes from last state
- No manual checkpointing needed

## Workflow Phases (Notebook 01)

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 1: PLANNING (iterative refinement)                   │
├─────────────────────────────────────────────────────────────┤
│  Loop until approved (max 3 iterations):                    │
│    1. GPT-4o creates/improves plan → research_plan.md       │
│    2. GPT-5.1 critiques plan → critique.md                  │
│    3. If score >= 8/10 or max iterations → proceed          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  PHASE 2: RESEARCH (execute the plan)                       │
├─────────────────────────────────────────────────────────────┤
│  GPT-4o reads plan, performs Tavily searches                │
│  Appends raw findings to research_plan.md                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  PHASE 3: SYNTHESIS (create final report)                   │
├─────────────────────────────────────────────────────────────┤
│  GPT-5.1 reads all findings from research_plan.md           │
│  Writes comprehensive report → research_report.md           │
└─────────────────────────────────────────────────────────────┘
```

## Parallel Sub-Agent Pattern (Notebook 02)

```python
from concurrent.futures import ThreadPoolExecutor

def research_sub_question(question, index):
    # Each sub-agent has its own conversation
    sub_agent = Agent(llm=llm, tools=[FileEditorTool, TavilySearch])
    sub_conversation = Conversation(agent=sub_agent, workspace=cwd)
    sub_conversation.send_message(f"Research: {question}. Write to findings_{index}.md")
    sub_conversation.run()
    return read_file(f"findings_{index}.md")

# Run all sub-questions in parallel
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(research_sub_question, q, i) for i, q in enumerate(questions)]
    results = [f.result() for f in futures]
```

## Error Handling Pattern

**Return errors as observations** - don't raise exceptions:

```python
class SearchExecutor(ToolExecutor):
    def __call__(self, action, conversation=None):
        try:
            result = tavily.search(query=action.query)
            return SearchObservation(results=result)
        except Exception as e:
            # ✅ Agent sees error and can adapt
            return SearchObservation(results=f"Search failed: {e}. Try a different query.")
```

**Why?**
- Raising exceptions crashes the agent loop
- Returning errors lets the agent retry or adjust strategy

## Observability

Built-in OpenTelemetry tracing via Laminar:

```python
# Just set the env var - no code changes needed
export LMNR_PROJECT_API_KEY=your-key
```

Traces include: agent steps, tool calls, LLM API calls, conversation lifecycle.

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Markdown files for state** | Human-readable, debuggable, no database needed |
| **Separate LLMs for different roles** | Different models excel at different tasks |
| **Iterative refinement loop** | Plans improve through critique feedback |
| **Native SDK persistence** | Event-sourcing handles checkpointing automatically |
| **Error as observation** | Keeps agent loop running, enables recovery |

## Extension Points

1. **Add new tools**: Follow the Action → Observation → Executor → ToolDefinition pattern
2. **Different search APIs**: Replace TavilyClient in SearchExecutor
3. **More sophisticated planning**: Add domain-specific critique criteria
4. **Additional output formats**: Modify synthesis prompts for JSON, HTML, etc.

## File Structure

```
openhands-deep-agent/
├── 00_simple_agent.ipynb      # SDK basics + MCP integration
├── 01_deep_research.ipynb     # 3-phase deep research workflow
├── 02_parallel_research.ipynb # Parallel sub-agent delegation
├── demo_fault_recovery.py     # Persistence/crash recovery demo
├── .conversations/            # SDK persistence (auto-created)
├── research_plan.md           # Generated: working plan + findings
├── critique.md                # Generated: plan evaluation
└── research_report.md         # Generated: final report
```
