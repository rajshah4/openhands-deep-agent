#!/usr/bin/env python3
"""
Basic Deep Research Agent with OpenHands SDK

This script demonstrates how to build a deep research agent using the OpenHands SDK.
It incorporates state-of-the-art patterns including:
- Task Decomposition
- Web Search Integration (Tavily API)
- Synthesis with Citations
- Structured Outputs using Pydantic

Usage:
    export LLM_API_KEY="your-api-key"
    export TAVILY_API_KEY="your-tavily-key"
    python 01_basic_deep_research.py
"""

import os
import json
import glob
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, SecretStr

from openhands.sdk import (
    LLM,
    Agent,
    Conversation,
    Tool,
    Action,
    Observation,
    ToolDefinition,
    ToolExecutor,
    TextContent,
    get_logger,
)
from openhands.sdk.tool import register_tool
from openhands.tools.file_editor import FileEditorTool
from openhands.tools.terminal import TerminalTool
from openhands.tools.task_tracker import TaskTrackerTool

# Import Tavily client
try:
    from tavily import TavilyClient
except ImportError:
    print("Please install tavily-python: pip install tavily-python")
    exit(1)

logger = get_logger(__name__)

# ============================================================================
# Data Models
# ============================================================================

class ResearchTask(BaseModel):
    """A single research subtask"""
    id: str = Field(description="Unique task identifier")
    title: str = Field(description="Brief task title")
    description: str = Field(description="Detailed task description")
    priority: int = Field(description="Priority level (1-5, 5 being highest)")
    status: str = Field(default="todo", description="Task status: todo, in_progress, done")
    dependencies: List[str] = Field(default_factory=list, description="IDs of tasks this depends on")

class ResearchPlan(BaseModel):
    """Complete research plan with decomposed tasks"""
    topic: str = Field(description="Main research topic")
    objective: str = Field(description="Research objective")
    tasks: List[ResearchTask] = Field(description="List of research tasks")
    created_at: datetime = Field(default_factory=datetime.now)

class SearchResult(BaseModel):
    """Structured search result"""
    title: str = Field(description="Result title")
    url: str = Field(description="Source URL")
    snippet: str = Field(description="Content snippet")
    relevance_score: float = Field(description="Relevance score (0-1)")
    
class ResearchFinding(BaseModel):
    """A synthesized research finding"""
    key_point: str = Field(description="Main finding or insight")
    evidence: List[str] = Field(description="Supporting evidence")
    sources: List[str] = Field(description="Source URLs")
    confidence: float = Field(description="Confidence level (0-1)")

class ResearchReport(BaseModel):
    """Complete research report"""
    topic: str = Field(description="Research topic")
    executive_summary: str = Field(description="Executive summary")
    findings: List[ResearchFinding] = Field(description="Key findings")
    methodology: str = Field(description="Research methodology")
    limitations: List[str] = Field(description="Research limitations")
    recommendations: List[str] = Field(description="Recommendations for further research")
    created_at: datetime = Field(default_factory=datetime.now)

# ============================================================================
# Custom Tools
# ============================================================================

# 1. Research Planner Tool
class PlannerAction(Action):
    """Action to create a research plan"""
    topic: str = Field(description="Research topic to plan")
    depth: str = Field(
        default="moderate", 
        description="Research depth: quick, moderate, or deep"
    )

class PlannerObservation(Observation):
    """Observation containing the research plan"""
    plan: ResearchPlan = Field(description="Generated research plan")
    
    @property
    def to_llm_content(self):
        tasks_summary = "\n".join([
            f"  {i+1}. [{t.priority}] {t.title}: {t.description[:100]}..."
            for i, t in enumerate(self.plan.tasks[:5])
        ])
        return [TextContent(text=f"""
Research Plan Created:
Topic: {self.plan.topic}
Objective: {self.plan.objective}
Number of tasks: {len(self.plan.tasks)}

Top tasks:
{tasks_summary}
""")]

class PlannerExecutor(ToolExecutor[PlannerAction, PlannerObservation]):
    """Executor that creates research plans"""
    
    def __init__(self, llm: LLM):
        self.llm = llm
    
    def __call__(self, action: PlannerAction, conversation=None) -> PlannerObservation:
        prompt = f"""
Create a detailed research plan for the topic: "{action.topic}"
Research depth: {action.depth}

Break this down into 5-8 specific, actionable research tasks.
Each task should have:
- A unique ID (e.g., task_1, task_2)
- Clear title and description
- Priority (1-5)
- Any dependencies on other tasks

Output the plan as a JSON object matching this structure:
{{
  "topic": "...",
  "objective": "...",
  "tasks": [
    {{
      "id": "task_1",
      "title": "...",
      "description": "...",
      "priority": 5,
      "dependencies": []
    }}
  ]
}}
"""
        
        response = self.llm.completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        try:
            plan_data = json.loads(response.choices[0].message.content)
            plan = ResearchPlan(**plan_data)
        except Exception as e:
            logger.error(f"Failed to parse plan: {e}")
            plan = ResearchPlan(
                topic=action.topic,
                objective=f"Research {action.topic} comprehensively",
                tasks=[
                    ResearchTask(
                        id="task_1",
                        title="Initial exploration",
                        description=f"Explore basic concepts and definitions related to {action.topic}",
                        priority=5
                    ),
                    ResearchTask(
                        id="task_2",
                        title="Deep dive research",
                        description=f"Research current state and recent developments in {action.topic}",
                        priority=4,
                        dependencies=["task_1"]
                    ),
                    ResearchTask(
                        id="task_3",
                        title="Synthesis and analysis",
                        description="Synthesize findings and identify key insights",
                        priority=3,
                        dependencies=["task_1", "task_2"]
                    )
                ]
            )
        
        return PlannerObservation(plan=plan)

PLANNER_DESCRIPTION = """
Research planning tool that decomposes complex research topics into structured tasks.
- Creates prioritized task lists with dependencies
- Supports different research depths (quick/moderate/deep)
- Outputs structured research plans
"""

class PlannerTool(ToolDefinition[PlannerAction, PlannerObservation]):
    """Research planner tool definition"""
    
    @classmethod
    def create(cls, conv_state, llm: LLM) -> List[ToolDefinition]:
        executor = PlannerExecutor(llm)
        return [
            cls(
                description=PLANNER_DESCRIPTION,
                action_type=PlannerAction,
                observation_type=PlannerObservation,
                executor=executor,
            )
        ]

# 2. Web Search Tool (Tavily API)
class SearchAction(Action):
    """Action to search the web"""
    query: str = Field(description="Search query")
    search_depth: str = Field(
        default="basic",
        description="Search depth: basic or advanced"
    )
    max_results: int = Field(
        default=5,
        description="Maximum number of results to return"
    )

class SearchObservation(Observation):
    """Observation containing search results"""
    results: List[SearchResult] = Field(description="Search results")
    query: str = Field(description="Original search query")
    
    @property
    def to_llm_content(self):
        if not self.results:
            return [TextContent(text=f"No results found for: {self.query}")]
        
        results_text = f"Search results for '{self.query}':\n\n"
        for i, result in enumerate(self.results[:5], 1):
            results_text += f"{i}. **{result.title}**\n"
            results_text += f"   URL: {result.url}\n"
            results_text += f"   {result.snippet[:200]}...\n\n"
        
        return [TextContent(text=results_text)]

class SearchExecutor(ToolExecutor[SearchAction, SearchObservation]):
    """Executor that performs web searches using Tavily"""
    
    def __init__(self, api_key: str):
        self.client = TavilyClient(api_key=api_key)
    
    def __call__(self, action: SearchAction, conversation=None) -> SearchObservation:
        try:
            response = self.client.search(
                query=action.query,
                search_depth=action.search_depth,
                max_results=action.max_results
            )
            
            results = []
            for item in response.get('results', []):
                result = SearchResult(
                    title=item.get('title', 'No title'),
                    url=item.get('url', ''),
                    snippet=item.get('content', '')[:500],
                    relevance_score=item.get('score', 0.0)
                )
                results.append(result)
            
            return SearchObservation(results=results, query=action.query)
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return SearchObservation(results=[], query=action.query)

SEARCH_DESCRIPTION = """
Web search tool powered by Tavily API.
- Searches the web for current information
- Returns structured results with titles, URLs, and snippets
- Supports basic and advanced search depths
- Use for finding recent information, research papers, news, etc.
"""

class SearchTool(ToolDefinition[SearchAction, SearchObservation]):
    """Web search tool definition"""
    
    @classmethod
    def create(cls, conv_state, api_key: str) -> List[ToolDefinition]:
        executor = SearchExecutor(api_key)
        return [
            cls(
                description=SEARCH_DESCRIPTION,
                action_type=SearchAction,
                observation_type=SearchObservation,
                executor=executor,
            )
        ]

# 3. Research Synthesizer Tool
class SynthesizerAction(Action):
    """Action to synthesize research findings"""
    topic: str = Field(description="Research topic")
    findings_file: str = Field(description="Path to file containing research findings")
    output_format: str = Field(
        default="markdown",
        description="Output format: markdown or json"
    )

class SynthesizerObservation(Observation):
    """Observation containing synthesized report"""
    report: ResearchReport = Field(description="Synthesized research report")
    report_path: str = Field(description="Path to saved report file")
    
    @property
    def to_llm_content(self):
        findings_summary = "\n".join([
            f"  • {f.key_point} (confidence: {f.confidence:.2f})"
            for f in self.report.findings[:3]
        ])
        return [TextContent(text=f"""
Research Report Synthesized:
Topic: {self.report.topic}

Executive Summary:
{self.report.executive_summary[:200]}...

Key Findings ({len(self.report.findings)} total):
{findings_summary}

Report saved to: {self.report_path}
""")]

class SynthesizerExecutor(ToolExecutor[SynthesizerAction, SynthesizerObservation]):
    """Executor that synthesizes research findings"""
    
    def __init__(self, llm: LLM):
        self.llm = llm
    
    def __call__(self, action: SynthesizerAction, conversation=None) -> SynthesizerObservation:
        try:
            with open(action.findings_file, 'r') as f:
                findings_content = f.read()
        except Exception as e:
            findings_content = f"Error reading findings: {e}"
        
        prompt = f"""
Synthesize the following research findings into a comprehensive report on "{action.topic}":

{findings_content}

Create a structured report with:
1. Executive summary (2-3 paragraphs)
2. Key findings with evidence and sources
3. Research methodology
4. Limitations
5. Recommendations

Output as JSON matching the ResearchReport structure.
"""
        
        response = self.llm.completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        try:
            report_data = json.loads(response.choices[0].message.content)
            report = ResearchReport(**report_data)
        except Exception as e:
            logger.error(f"Failed to parse report: {e}")
            report = ResearchReport(
                topic=action.topic,
                executive_summary="Research synthesis in progress...",
                findings=[],
                methodology="Web search and content analysis",
                limitations=["Limited to available online sources"],
                recommendations=["Further research recommended"]
            )
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"research_report_{timestamp}.{action.output_format}"
        
        if action.output_format == "markdown":
            markdown_content = self._generate_markdown_report(report)
            with open(report_filename, 'w') as f:
                f.write(markdown_content)
        else:
            with open(report_filename, 'w') as f:
                json.dump(report.model_dump(), f, indent=2, default=str)
        
        return SynthesizerObservation(report=report, report_path=report_filename)
    
    def _generate_markdown_report(self, report: ResearchReport) -> str:
        """Generate markdown version of the report"""
        markdown = f"""# Research Report: {report.topic}

**Generated:** {report.created_at.strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

{report.executive_summary}

## Key Findings

"""
        for i, finding in enumerate(report.findings, 1):
            markdown += f"""### Finding {i}: {finding.key_point}

**Confidence:** {finding.confidence:.2f}

**Evidence:**
"""
            for evidence in finding.evidence:
                markdown += f"- {evidence}\n"
            
            markdown += "\n**Sources:**\n"
            for source in finding.sources:
                markdown += f"- [{source}]({source})\n"
            markdown += "\n"
        
        markdown += f"""## Methodology

{report.methodology}

## Limitations

"""
        for limitation in report.limitations:
            markdown += f"- {limitation}\n"
        
        markdown += "\n## Recommendations\n\n"
        for rec in report.recommendations:
            markdown += f"- {rec}\n"
        
        return markdown

SYNTHESIZER_DESCRIPTION = """
Research synthesis tool that combines findings into structured reports.
- Aggregates research findings with citations
- Creates executive summaries
- Identifies key insights and patterns
- Outputs markdown or JSON reports
"""

class SynthesizerTool(ToolDefinition[SynthesizerAction, SynthesizerObservation]):
    """Research synthesizer tool definition"""
    
    @classmethod
    def create(cls, conv_state, llm: LLM) -> List[ToolDefinition]:
        executor = SynthesizerExecutor(llm)
        return [
            cls(
                description=SYNTHESIZER_DESCRIPTION,
                action_type=SynthesizerAction,
                observation_type=SynthesizerObservation,
                executor=executor,
            )
        ]

# ============================================================================
# Research Orchestrator
# ============================================================================

class ResearchOrchestrator:
    """Orchestrates the deep research workflow"""
    
    def __init__(self, agent: Agent, workspace: str):
        self.agent = agent
        self.workspace = workspace
        self.conversation = None
        self.research_state = {
            "plan": None,
            "findings": [],
            "report": None
        }
    
    def research(self, topic: str, depth: str = "moderate"):
        """Execute the complete research workflow"""
        print(f"\n🔬 Starting deep research on: {topic}")
        print(f"   Research depth: {depth}")
        print("=" * 60)
        
        self.conversation = Conversation(
            agent=self.agent,
            workspace=self.workspace
        )
        
        # Phase 1: Planning
        print("\n📋 Phase 1: Research Planning")
        planning_prompt = f"""
I need to conduct {depth} research on the topic: "{topic}"

Please:
1. Use the research planner tool to create a detailed research plan
2. Use the task tracker to organize the research tasks
3. Identify the top 3 priority tasks to start with
"""
        self.conversation.send_message(planning_prompt)
        self.conversation.run()
        
        # Phase 2: Research Execution
        print("\n🔍 Phase 2: Research Execution")
        research_prompt = f"""
Now let's execute the research plan:

1. For each high-priority task, use the web search tool to find relevant information
2. Save the search results and key findings to a file called 'research_findings.json'
3. Organize findings by subtopic with proper citations
4. Update the task tracker as you complete each task

Focus on finding:
- Current state and recent developments
- Key concepts and definitions
- Expert opinions and analysis
- Relevant statistics and data

Use search queries that are specific and targeted to get the best results.
"""
        self.conversation.send_message(research_prompt)
        self.conversation.run()
        
        # Phase 3: Synthesis
        print("\n📝 Phase 3: Synthesis and Report Generation")
        synthesis_prompt = f"""
Now synthesize all the research findings:

1. Use the synthesizer tool to create a comprehensive research report
2. Input file: 'research_findings.json'
3. Output format: markdown
4. Ensure the report includes:
   - Executive summary
   - Key findings with evidence
   - Proper citations
   - Limitations and recommendations

After creating the report, provide a brief summary of the key insights.
"""
        self.conversation.send_message(synthesis_prompt)
        self.conversation.run()
        
        print("\n✅ Research completed!")
        print("=" * 60)
        
        # Get metrics
        metrics = self.conversation.conversation_stats.get_combined_metrics()
        print(f"\n📊 Research Metrics:")
        print(f"   Total tokens: {metrics.total_tokens:,}")
        print(f"   Total cost: ${metrics.accumulated_cost:.4f}")
        print(f"   LLM calls: {metrics.llm_calls}")
        print(f"   Tool calls: {metrics.tool_calls}")
        
        return self.conversation

# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Main execution function"""
    
    # Check environment variables
    llm_api_key = os.getenv("LLM_API_KEY")
    if not llm_api_key:
        print("Error: LLM_API_KEY environment variable not set")
        print("Please set it with: export LLM_API_KEY='your-api-key'")
        return
    
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if not tavily_api_key:
        print("Warning: TAVILY_API_KEY not set, web search will not be available")
        print("Get a free API key at: https://tavily.com")
    
    # Initialize LLM
    llm = LLM(
        model=os.getenv("LLM_MODEL", "anthropic/claude-sonnet-4-5-20250929"),
        api_key=SecretStr(llm_api_key),
        base_url=os.getenv("LLM_BASE_URL"),
        usage_id="research-agent"
    )
    
    # Register custom tools
    def create_research_tools(conv_state) -> List[ToolDefinition]:
        """Factory function to create research tools"""
        tools = []
        
        # Add planner tool
        tools.extend(PlannerTool.create(conv_state, llm))
        
        # Add synthesizer tool
        tools.extend(SynthesizerTool.create(conv_state, llm))
        
        # Add search tool if API key available
        if tavily_api_key:
            tools.extend(SearchTool.create(conv_state, tavily_api_key))
        
        return tools
    
    register_tool("ResearchTools", create_research_tools)
    
    # Create agent
    tools = [
        Tool(name=TerminalTool.name),
        Tool(name=FileEditorTool.name),
        Tool(name=TaskTrackerTool.name),
        Tool(name="ResearchTools"),
    ]
    
    agent = Agent(
        llm=llm,
        tools=tools,
    )
    
    print("Research agent created with tools:")
    for tool in tools:
        print(f"  - {tool.name}")
    
    # Create orchestrator
    orchestrator = ResearchOrchestrator(agent, os.getcwd())
    
    # Example research topic
    research_topic = "The impact of large language models on software development practices"
    
    # Run the research
    conversation = orchestrator.research(
        topic=research_topic,
        depth="moderate"
    )
    
    # Display the report
    print("\n📄 Generated Report:")
    print("-" * 60)
    
    report_files = glob.glob("research_report_*.md")
    if report_files:
        latest_report = max(report_files, key=os.path.getctime)
        print(f"Report saved to: {latest_report}\n")
        
        with open(latest_report, 'r') as f:
            content = f.read()
            print(content[:1000] + "...\n\n[Report truncated for display]")
    else:
        print("No research report found. The synthesis may have encountered an issue.")

if __name__ == "__main__":
    main()