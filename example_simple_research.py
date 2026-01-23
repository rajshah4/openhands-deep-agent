#!/usr/bin/env python3
"""
Simple example demonstrating the deep research agent architecture.

This is a minimal example showing:
1. Task decomposition (manual for simplicity)
2. Web search using Tavily
3. Basic synthesis

Usage:
    export TAVILY_API_KEY="your-key"
    python example_simple_research.py
"""

import os
import json
from datetime import datetime
from tavily import TavilyClient

def decompose_topic(topic):
    """Simple task decomposition"""
    return [
        f"What are the key concepts and definitions related to {topic}?",
        f"What are the recent developments and trends in {topic}?",
        f"What are the main challenges and opportunities in {topic}?",
    ]

def search_web(query, api_key):
    """Search using Tavily API"""
    client = TavilyClient(api_key=api_key)
    try:
        response = client.search(query=query, max_results=3)
        return response.get('results', [])
    except Exception as e:
        print(f"Search error: {e}")
        return []

def synthesize_findings(topic, all_results):
    """Basic synthesis of findings"""
    report = {
        "topic": topic,
        "generated_at": datetime.now().isoformat(),
        "summary": f"Research findings on {topic}",
        "findings": [],
        "sources": []
    }
    
    for query, results in all_results.items():
        finding = {
            "question": query,
            "insights": []
        }
        
        for result in results:
            finding["insights"].append({
                "title": result.get('title', ''),
                "content": result.get('content', '')[:200] + "...",
                "url": result.get('url', '')
            })
            report["sources"].append(result.get('url', ''))
        
        report["findings"].append(finding)
    
    return report

def main():
    # Check for API key
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        print("Error: TAVILY_API_KEY not set")
        print("Get a free key at: https://tavily.com")
        return
    
    # Research topic
    topic = "AI agents in software development"
    print(f"🔬 Researching: {topic}\n")
    
    # Phase 1: Decompose
    print("📋 Phase 1: Task Decomposition")
    tasks = decompose_topic(topic)
    for i, task in enumerate(tasks, 1):
        print(f"  {i}. {task}")
    
    # Phase 2: Search
    print("\n🔍 Phase 2: Web Search")
    all_results = {}
    for task in tasks:
        print(f"  Searching: {task[:50]}...")
        results = search_web(task, api_key)
        all_results[task] = results
        print(f"    Found {len(results)} results")
    
    # Phase 3: Synthesize
    print("\n📝 Phase 3: Synthesis")
    report = synthesize_findings(topic, all_results)
    
    # Save report
    filename = f"simple_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Report saved to: {filename}")
    
    # Display summary
    print("\n📊 Summary:")
    print(f"  Total findings: {len(report['findings'])}")
    print(f"  Total sources: {len(set(report['sources']))}")
    print("\n  Sample insights:")
    for finding in report['findings'][:2]:
        print(f"\n  Q: {finding['question'][:60]}...")
        for insight in finding['insights'][:1]:
            print(f"     {insight['title']}")

if __name__ == "__main__":
    main()