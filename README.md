# openhands-deep-agent

## Overview

This repository demonstrates how to build **deep research agents** using the [OpenHands SDK](https://docs.openhands.dev/sdk). It showcases state-of-the-art patterns for multi-agent orchestration, task decomposition, and knowledge synthesis.

## Status

🔬 **Active Development** - Deep research in progress

---

## Notebooks

### 1. `01_basic_deep_research.ipynb` - Basic Deep Research Agent
A complete implementation showing the core concepts:
- **Planner**: Decomposes research topics into subtasks using LLM
- **Searcher**: Web search via Tavily API (direct integration)
- **Synthesizer**: Combines findings into a coherent report with citations
- **Orchestration loop**: Manages the complete research workflow
- **Structured outputs**: All data validated with Pydantic models

### 2. `02_advanced_deep_research.ipynb` - Full-Featured Deep Research Agent *(Coming Soon)*
Advanced implementation with all architectural patterns:
- Multi-agent delegation with sub-agent spawning
- Persistent state management (files + conversation persistence)
- Structured Pydantic outputs with validation
- Iterative refinement and error handling
- Full controller/orchestrator pattern

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONTROLLER/ORCHESTRATOR                       │
│              (Main agent with sub-agent delegation)              │
└─────────────────────┬───────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│   PLANNER     │ │   SEARCHER    │ │  SYNTHESIZER  │
│   AGENT       │ │   AGENT       │ │    AGENT      │
├───────────────┤ ├───────────────┤ ├───────────────┤
│ • Decompose   │ │ • Web search  │ │ • Aggregate   │
│   research    │ │   (Tavily MCP)│ │   findings    │
│ • Task list   │ │ • Structured  │ │ • Citations   │
│ • Priorities  │ │   snippets    │ │ • Synthesis   │
└───────────────┘ └───────────────┘ └───────────────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          ▼
              ┌───────────────────────┐
              │  STATE PERSISTENCE    │
              │  (Files + Conversation│
              │   Persistence)        │
              └───────────────────────┘
```

---

## Key Patterns Demonstrated

| Pattern | Basic Notebook | Advanced Notebook |
|---------|:-------------:|:-----------------:|
| Task Decomposition | ✅ | ✅ |
| Web Search (Tavily API) | ✅ | ✅ |
| Synthesis with Citations | ✅ | ✅ |
| Custom Tools (Pydantic) | ✅ | ✅ |
| Orchestration Loop | ✅ | ✅ |
| Sub-agent Delegation | ❌ | ✅ |
| State Persistence | ❌ | ✅ |
| Iterative Refinement | ❌ | ✅ |
| Error Recovery | ❌ | ✅ |

---

## Getting Started

**Quick Start**: See [QUICKSTART.md](QUICKSTART.md) for a 5-minute setup guide.

### Prerequisites
- Python 3.11+
- [uv package manager](https://docs.astral.sh/uv/) (optional)
- LLM API key (Anthropic, OpenAI, or [OpenHands Cloud](https://app.all-hands.dev))
- Tavily API key for web search

### Installation

```bash
# Install OpenHands SDK and dependencies
pip install openhands-sdk openhands-tools tavily-python

# Set environment variables
export LLM_API_KEY="your-llm-api-key"
export TAVILY_API_KEY="your-tavily-api-key"
```

### Run the Notebooks

```bash
# Launch Jupyter
jupyter notebook

# Or run the Python script directly
python 01_basic_deep_research.py

# Or use uv if you prefer
uv run python 01_basic_deep_research.py
```

---

## Documentation

- [QUICKSTART.md](QUICKSTART.md) - Get started in 5 minutes
- [ARCHITECTURE.md](ARCHITECTURE.md) - Detailed architecture and design patterns
- [01_basic_deep_research.ipynb](01_basic_deep_research.ipynb) - Interactive notebook with full implementation

---

## References

- [OpenHands SDK Documentation](https://docs.openhands.dev/sdk)
- [OpenHands SDK GitHub](https://github.com/OpenHands/software-agent-sdk)
- [Tavily API](https://tavily.com) - Get your free API key
- [Pydantic Documentation](https://docs.pydantic.dev/) - For structured data validation