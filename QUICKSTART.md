# Quick Start Guide

Get up and running with the OpenHands Deep Research Agent in 5 minutes!

## Prerequisites

- Python 3.11+
- API Keys:
  - LLM API key (Anthropic, OpenAI, or [OpenHands Cloud](https://app.all-hands.dev))
  - [Tavily API key](https://tavily.com) for web search (free tier available)

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/openhands-deep-agent.git
cd openhands-deep-agent

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Set your API keys:

```bash
# Required: LLM API key
export LLM_API_KEY="your-llm-api-key"

# Required: Tavily API key for web search
export TAVILY_API_KEY="your-tavily-api-key"

# Optional: Specify model (defaults to Claude Sonnet)
export LLM_MODEL="anthropic/claude-sonnet-4-5-20250929"
```

## Run Your First Research

### Option 1: Python Script (Quickest)

```bash
python 01_basic_deep_research.py
```

This will research "The impact of large language models on software development practices" and generate a markdown report.

### Option 2: Jupyter Notebook (Interactive)

```bash
jupyter notebook 01_basic_deep_research.ipynb
```

Run cells sequentially to see each phase of the research process.

### Option 3: Simple Example (Understanding the Basics)

```bash
python example_simple_research.py
```

This minimal example shows the core concepts without the full agent framework.

## What to Expect

The agent will:

1. **Plan** - Break down your topic into research tasks
2. **Search** - Find relevant information using web search
3. **Synthesize** - Combine findings into a structured report

Output files:
- `research_findings.json` - Raw research data
- `research_report_[timestamp].md` - Final formatted report

## Customizing Your Research

### Change the Topic

Edit the research topic in the script:

```python
research_topic = "Your topic here"
```

### Adjust Research Depth

Choose from three levels:

```python
orchestrator.research(
    topic=research_topic,
    depth="quick"     # Options: quick, moderate, deep
)
```

### Modify Search Parameters

In the SearchAction:

```python
search_depth="advanced"  # More comprehensive results
max_results=10          # More results per query
```

## Common Issues

### "TAVILY_API_KEY not set"
- Get a free API key at [tavily.com](https://tavily.com)
- Set it: `export TAVILY_API_KEY="your-key"`

### "LLM_API_KEY not set"
- Get an API key from your LLM provider
- Or use [OpenHands Cloud](https://app.all-hands.dev) for easy access

### Import errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Use Python 3.11 or higher

## Next Steps

1. **Explore the Architecture**: Read [ARCHITECTURE.md](ARCHITECTURE.md)
2. **Modify the Tools**: Add your own custom tools
3. **Try Different Topics**: Test with various research subjects
4. **Build Advanced Features**: See the roadmap in README.md

## Getting Help

- Check the [OpenHands SDK docs](https://docs.openhands.dev/sdk)
- Join the [OpenHands Slack](https://join.slack.com/t/openhandscommunity/shared_invite/zt-2x1x1x1x1)
- Open an issue on GitHub

Happy researching! 🔬