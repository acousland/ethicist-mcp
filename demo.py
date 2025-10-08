#!/usr/bin/env python3
"""
Quick demo of the Ethicist MCP Server capabilities.
Run this to see example outputs from each tool.
"""

import asyncio
from ethicist_mcp.server import (
    list_tools,
    list_resources,
    list_prompts,
    call_tool,
    read_resource,
    get_prompt,
)
from pydantic import AnyUrl


async def demo():
    """Run a quick demo of the server capabilities."""
    
    print("\n" + "=" * 80)
    print("ETHICIST MCP SERVER - INTERACTIVE DEMO")
    print("=" * 80)
    
    # Demo 1: Ethical Scenario Analysis
    print("\n📊 DEMO 1: Analyzing an Ethical Scenario")
    print("-" * 80)
    scenario = "A hospital AI must prioritize patients for limited ICU beds during a pandemic"
    print(f"Scenario: {scenario}\n")
    
    result = await call_tool(
        name="analyze_ethical_scenario",
        arguments={
            "scenario": scenario,
            "frameworks": ["utilitarian", "care"]
        }
    )
    print(result[0].text[:600] + "...\n")
    
    # Demo 2: AI System Evaluation
    print("\n🔍 DEMO 2: Evaluating an AI System")
    print("-" * 80)
    print("System: Resume screening AI for tech recruitment\n")
    
    result = await call_tool(
        name="evaluate_ai_system",
        arguments={
            "system_description": "An AI that ranks job candidates based on resumes",
            "use_case": "Tech company recruitment",
            "stakeholders": ["job seekers", "hiring managers", "HR team"]
        }
    )
    print(result[0].text[:600] + "...\n")
    
    # Demo 3: Bias Check
    print("\n⚠️  DEMO 3: Checking for Bias")
    print("-" * 80)
    print("Context: Training data from historical hiring decisions\n")
    
    result = await call_tool(
        name="check_bias",
        arguments={
            "context": "Historical hiring data from the past 20 years",
            "bias_types": ["selection", "representation"]
        }
    )
    print(result[0].text[:600] + "...\n")
    
    # Demo 4: Generate Guidelines
    print("\n📋 DEMO 4: Generating Ethical Guidelines")
    print("-" * 80)
    print("Project: Healthcare diagnostic AI\n")
    
    result = await call_tool(
        name="generate_ethical_guidelines",
        arguments={
            "project_type": "healthcare AI",
            "risk_level": "high",
            "regulations": ["HIPAA", "FDA"]
        }
    )
    print(result[0].text[:600] + "...\n")
    
    # Demo 5: Transparency Assessment
    print("\n🔎 DEMO 5: Assessing Transparency")
    print("-" * 80)
    print("System: Neural network for loan approval\n")
    
    result = await call_tool(
        name="assess_transparency",
        arguments={
            "system_type": "neural network",
            "explanation_method": "SHAP values",
            "stakeholder_needs": ["applicants", "regulators"]
        }
    )
    print(result[0].text[:600] + "...\n")
    
    # Demo 6: Resource Access
    print("\n📚 DEMO 6: Accessing Ethical Resources")
    print("-" * 80)
    print("Resource: AI Ethics Guidelines\n")
    
    content = await read_resource(uri=AnyUrl("ethicist://guidelines/ai-ethics"))
    import json
    guidelines = json.loads(content)
    print("AI Ethics Guidelines:")
    for key, value in list(guidelines.items())[:3]:
        print(f"  • {key.replace('_', ' ').title()}: {value}")
    print(f"  ... and {len(guidelines) - 3} more\n")
    
    # Demo 7: Prompt Example
    print("\n💭 DEMO 7: Using an Ethical Prompt")
    print("-" * 80)
    print("Prompt: Ethical Decision Making\n")
    
    prompt_result = await get_prompt(
        name="ethical_decision_making",
        arguments={"situation": "deploying an AI surveillance system"}
    )
    print(f"Description: {prompt_result.description}")
    print(f"Message preview: {prompt_result.messages[0].content.text[:400]}...\n")
    
    # Summary
    print("\n" + "=" * 80)
    print("DEMO COMPLETE!")
    print("=" * 80)
    print("\nThe Ethicist MCP Server provides:")
    
    tools = await list_tools()
    resources = await list_resources()
    prompts = await list_prompts()
    
    print(f"  ✓ {len(tools)} comprehensive ethical analysis tools")
    print(f"  ✓ {len(resources)} ethical knowledge resources")
    print(f"  ✓ {len(prompts)} guided reasoning prompts")
    print(f"  ✓ 4 major ethical frameworks")
    print(f"  ✓ 8 AI ethics principles")
    print("\nReady to integrate into your AI development workflow!")
    print("See EXAMPLES.md for more detailed usage examples.\n")


if __name__ == "__main__":
    print("\nStarting Ethicist MCP Server Demo...")
    print("This will showcase the key capabilities of the server.\n")
    asyncio.run(demo())
