# openhands-deep-agent

## Overview

This repository demonstrates how to build **deep research agents** using the [OpenHands SDK](https://docs.openhands.dev/sdk). It showcases multi-agent orchestration, iterative refinement, and knowledge synthesis patterns.

## Status

✅ **Working Examples** - Three notebooks (simple → deep → parallel)

---

## Notebooks

### 1. `00_simple_agent.ipynb` - Getting Started with OpenHands SDK

A minimal introduction to the OpenHands SDK:
- Setting up LLM and environment
- Creating custom tools (Tavily search with Pydantic)
- Understanding the Action → Observation → Executor → ToolDefinition pattern
- Running a basic research query

**Best for:** Learning the SDK basics before diving into advanced patterns.

### 2. `01_deep_research.ipynb` - Deep Research Agent (3-Phase Workflow)

A complete deep research implementation with multi-agent collaboration:

| Phase | Agent | Output |
|-------|-------|--------|
| **1. Planning** | GPT-4o creates plan → GPT-5.1 critiques → iterate until approved | `research_plan.md` |
| **2. Research** | GPT-4o executes Tavily searches, gathers raw findings | Updated `research_plan.md` |
| **3. Synthesis** | GPT-5.1 synthesizes all findings into comprehensive report | `research_report.md` |

**Features:**
- ✅ Multi-agent collaboration (GPT-4o + GPT-5.1)
- ✅ Iterative plan refinement with scoring
- ✅ **Checkpointing** - Resume from crash/interrupt
- ✅ **Observability** - Laminar tracing support
- ✅ Professional report synthesis with citations

### 3. `02_parallel_research.ipynb` - Parallel Sub-Agent Research

Advanced pattern with parallel sub-agent delegation:
- Spawn dedicated sub-agents for each sub-question
- Execute searches in parallel using `ThreadPoolExecutor`
- Isolated context per sub-question (each writes to own file)
- Aggregate results for final synthesis with GPT-5.1

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 1: PLANNING (with iterative critique)                │
├─────────────────────────────────────────────────────────────┤
│  GPT-4o creates plan → GPT-5.1 critiques → improve → loop   │
│  Output: research_plan.md (approved sub-questions)          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  PHASE 2: RESEARCH (gather raw findings)                    │
├─────────────────────────────────────────────────────────────┤
│  GPT-4o executes Tavily searches for each sub-question      │
│  Output: research_plan.md (with raw findings + URLs)        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  PHASE 3: SYNTHESIS (comprehensive report)                  │
├─────────────────────────────────────────────────────────────┤
│  GPT-5.1 reads all findings and writes professional report  │
│  Output: research_report.md                                 │
│    - Executive Summary                                      │
│    - Key Findings (by theme)                                │
│    - Analysis & Implications                                │
│    - References with URLs                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Patterns Demonstrated

| Pattern | Notebook 00 | Notebook 01 | Notebook 02 |
|---------|:-----------:|:-----------:|:-----------:|
| Custom Tools (Pydantic) | ✅ | ✅ | ✅ |
| Web Search (Tavily) | ✅ | ✅ | ✅ |
| Task Decomposition | ❌ | ✅ | ✅ |
| Multi-Agent Collaboration | ❌ | ✅ | ✅ |
| Iterative Refinement | ❌ | ✅ | ✅ |
| Checkpointing / Resume | ❌ | ✅ | ✅ |
| Observability (Laminar) | ❌ | ✅ | ✅ |
| **Sub-Agent Parallelization** | ❌ | ❌ | ✅ |

---

## Getting Started

### Prerequisites
- Python 3.11+
- LLM API key (OpenAI recommended for GPT-4o and GPT-5.1)
- Tavily API key for web search

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install directly
pip install openhands-sdk python-dotenv tavily-python
```

### Environment Variables

Copy the example environment file and add your API keys:

```bash
cp env.example .env
```

Then edit `.env` with your values:

| Variable | Required | Description |
|----------|:--------:|-------------|
| `LLM_API_KEY` | ✅ | Your LLM API key (OpenAI, Anthropic, etc.) |
| `TAVILY_API_KEY` | ✅ | Your Tavily API key for web search |
| `LLM_MODEL` | ❌ | Model to use (defaults to `openai/gpt-4o`) |
| `LLM_BASE_URL` | ❌ | Custom LLM endpoint URL (optional) |
| `LMNR_PROJECT_API_KEY` | ❌ | Laminar API key for observability ([laminar.sh](https://laminar.sh)) |

#### Example Configuration (OpenAI)

```bash
LLM_API_KEY=sk-your-openai-api-key
LLM_MODEL=openai/gpt-4o
TAVILY_API_KEY=tvly-your-tavily-key
LMNR_PROJECT_API_KEY=your-laminar-key  # Optional: for tracing
```

### Run the Notebooks

```bash
# Launch Jupyter
jupyter notebook

# Start with notebook 00 to learn the basics
# Then run notebook 01 for the full deep research workflow
```

---

## Output Files

When you run `01_deep_research.ipynb`:

| File | Purpose |
|------|---------|
| `research_plan.md` | Working document with sub-questions + raw findings |
| `critique.md` | Plan evaluation feedback (for debugging) |
| `research_report.md` | **Final deliverable** - comprehensive research report |
| `checkpoint.json` | Resume state (auto-deleted on success) |

When you run `02_parallel_research.ipynb`:

| File | Purpose |
|------|---------|
| `findings_1.md` ... `findings_N.md` | Individual sub-agent findings |
| `parallel_findings.md` | Aggregated raw findings |
| `parallel_report.md` | **Final deliverable** - synthesized research report |

---

## Observability

The SDK has built-in [OpenTelemetry tracing](https://docs.openhands.dev/sdk/guides/observability). Set `LMNR_PROJECT_API_KEY` to enable Laminar tracing:

- Agent execution steps
- Tool calls (Tavily searches)
- LLM API calls
- Conversation lifecycle

View traces at [laminar.sh](https://laminar.sh) (free tier available).

---

## References

- [OpenHands SDK Documentation](https://docs.openhands.dev/sdk)
- [OpenHands Iterative Refinement Guide](https://docs.openhands.dev/sdk/guides/iterative-refinement)
- [OpenHands Observability Guide](https://docs.openhands.dev/sdk/guides/observability)
- [Tavily API](https://tavily.com) - Get your free API key
- [Laminar](https://laminar.sh) - AI observability platform