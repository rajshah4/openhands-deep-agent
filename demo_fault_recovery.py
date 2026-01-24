#!/usr/bin/env python3
"""
Fault Recovery Demo - OpenHands SDK Persistence

This script demonstrates the SDK's persistence feature:
1. Run it: python demo_fault_recovery.py
2. Kill it mid-way: Ctrl+C (or kill the process)
3. Run it again: python demo_fault_recovery.py
4. Watch it RESUME from where it left off!

The magic: persistence_dir + conversation_id
"""

import os
import uuid
import time
from dotenv import load_dotenv
load_dotenv()

from typing import List
from pydantic import Field
from tavily import TavilyClient
from openhands.sdk import LLM, Agent, Conversation, Tool, Action, Observation, ToolDefinition, TextContent
from openhands.sdk.tool import register_tool, ToolExecutor
from openhands.tools.file_editor import FileEditorTool

# ============================================
# Setup
# ============================================

print("=" * 60)
print("🔄 FAULT RECOVERY DEMO - OpenHands SDK Persistence")
print("=" * 60)
print("\nThis demo shows how the SDK automatically saves state.")
print("You can KILL this script (Ctrl+C) and restart it - ")
print("it will resume from where it left off!\n")

# Create LLM
llm = LLM(
    model=os.getenv("LLM_MODEL", "openai/gpt-4o"),
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL", None),
)

# Create Tavily tool
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

class SearchAction(Action):
    query: str = Field(description="Search query")

class SearchObservation(Observation):
    results: str = Field(description="Results")
    @property
    def to_llm_content(self): return [TextContent(text=self.results)]

class SearchExecutor(ToolExecutor):
    def __call__(self, action: SearchAction, conversation=None) -> SearchObservation:
        print(f"    🔍 Searching: {action.query[:50]}...")
        time.sleep(1)  # Slow down so you can see progress
        try:
            r = tavily.search(query=action.query, max_results=3)
            text = "\n".join([f"- {x['title']}" for x in r['results']])
            return SearchObservation(results=text or "No results")
        except Exception as e:
            return SearchObservation(results=f"Search failed: {e}")

class SearchTool(ToolDefinition[SearchAction, SearchObservation]):
    @classmethod
    def create(cls, conv_state) -> List["SearchTool"]:
        return [cls(description="Web search via Tavily",
                    action_type=SearchAction, observation_type=SearchObservation, 
                    executor=SearchExecutor())]

register_tool("TavilySearch", SearchTool.create)

# Create Agent
agent = Agent(
    llm=llm,
    tools=[
        Tool(name=FileEditorTool.name),
        Tool(name="TavilySearch"),
    ],
)

# ============================================
# Persistence Configuration
# ============================================

PERSISTENCE_DIR = "./.conversations"
SESSION_NAME = "fault-recovery-demo"
SESSION_ID = uuid.uuid5(uuid.NAMESPACE_DNS, SESSION_NAME)

session_path = os.path.join(PERSISTENCE_DIR, SESSION_ID.hex)

print("-" * 60)
if os.path.exists(session_path):
    print(f"🔄 RESUMING existing session!")
    print(f"   Found saved state at: {session_path}")
    print(f"   The agent will continue where it left off.")
else:
    print(f"📝 STARTING fresh session")
    print(f"   State will be saved to: {session_path}")
print("-" * 60)

# ============================================
# Create Conversation with Persistence
# ============================================

conversation = Conversation(
    agent=agent,
    workspace=os.getcwd(),
    persistence_dir=PERSISTENCE_DIR,
    conversation_id=SESSION_ID,
)

# ============================================
# Run a Multi-Step Research Task
# ============================================

RESEARCH_PROMPT = """
Research "AI agents in 2025" by doing these 5 steps IN ORDER:

1. First, search for "latest AI agent frameworks 2025"
2. Then, search for "autonomous AI agents breakthroughs"  
3. Then, search for "multi-agent collaboration systems"
4. Then, search for "AI agent safety concerns 2025"
5. Finally, write a brief summary to `demo_findings.md`

Do each step one at a time. After each search, briefly note what you found.
This is a SLOW, DELIBERATE process - take your time with each step.
"""

print("\n📋 Sending research task (5 steps)...")
print("   💡 TIP: Try killing this script (Ctrl+C) mid-way, then restart!\n")

conversation.send_message(RESEARCH_PROMPT)

try:
    conversation.run()
    print("\n" + "=" * 60)
    print("✅ RESEARCH COMPLETE!")
    print("=" * 60)
    
    # Show results
    if os.path.exists("demo_findings.md"):
        print("\n📄 Results saved to demo_findings.md:")
        print("-" * 40)
        with open("demo_findings.md", "r") as f:
            print(f.read()[:500] + "..." if len(f.read()) > 500 else f.read())
    
except KeyboardInterrupt:
    print("\n\n" + "=" * 60)
    print("⚠️  INTERRUPTED! (Ctrl+C detected)")
    print("=" * 60)
    print(f"\n💾 State saved to: {session_path}")
    print("\n👉 Run this script again to RESUME from this point!")
    print("   python demo_fault_recovery.py\n")

print("\n🧹 To start fresh, delete the session folder:")
print(f"   rm -rf {session_path}\n")
