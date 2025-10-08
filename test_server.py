#!/usr/bin/env python3
"""
Test script to verify the Ethicist MCP Server functionality.
"""

import asyncio
import json
from ethicist_mcp.server import app, ETHICAL_FRAMEWORKS, AI_ETHICS_GUIDELINES


async def test_server():
    """Test the MCP server components."""
    print("=" * 80)
    print("ETHICIST MCP SERVER TEST")
    print("=" * 80)
    
    # Import the handler functions directly
    from ethicist_mcp.server import list_tools, list_resources, list_prompts, call_tool, read_resource, get_prompt
    from pydantic import AnyUrl
    
    # Test 1: List Tools
    print("\n1. Testing list_tools()...")
    tools = await list_tools()
    print(f"✓ Found {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description[:60]}...")
    
    # Test 2: List Resources
    print("\n2. Testing list_resources()...")
    resources = await list_resources()
    print(f"✓ Found {len(resources)} resources:")
    for resource in resources:
        print(f"  - {resource.name} ({resource.uri})")
    
    # Test 3: List Prompts
    print("\n3. Testing list_prompts()...")
    prompts = await list_prompts()
    print(f"✓ Found {len(prompts)} prompts:")
    for prompt in prompts:
        print(f"  - {prompt.name}: {prompt.description[:60]}...")
    
    # Test 4: Call a tool
    print("\n4. Testing call_tool() with analyze_ethical_scenario...")
    result = await call_tool(
        name="analyze_ethical_scenario",
        arguments={
            "scenario": "An AI system must decide who gets priority access to limited medical resources",
            "frameworks": ["utilitarian", "deontological"]
        }
    )
    print(f"✓ Tool returned {len(result)} content item(s)")
    print(f"  First 200 chars: {result[0].text[:200]}...")
    
    # Test 5: Read a resource
    print("\n5. Testing read_resource()...")
    resource_content = await read_resource(
        uri=AnyUrl("ethicist://frameworks/all")
    )
    print(f"✓ Resource content length: {len(resource_content)} chars")
    frameworks = json.loads(resource_content)
    print(f"  Frameworks loaded: {', '.join(frameworks.keys())}")
    
    # Test 6: Get a prompt
    print("\n6. Testing get_prompt()...")
    prompt_result = await get_prompt(
        name="ethical_decision_making",
        arguments={"situation": "hiring an AI engineer"}
    )
    print(f"✓ Prompt has {len(prompt_result.messages)} message(s)")
    print(f"  Description: {prompt_result.description}")
    
    # Test 7: Verify data structures
    print("\n7. Verifying data structures...")
    print(f"✓ Ethical Frameworks: {len(ETHICAL_FRAMEWORKS)} frameworks")
    print(f"✓ AI Ethics Guidelines: {len(AI_ETHICS_GUIDELINES)} guidelines")
    
    print("\n" + "=" * 80)
    print("ALL TESTS PASSED!")
    print("=" * 80)
    
    # Print summary
    print("\nServer Summary:")
    print(f"  • {len(tools)} Tools available for ethical analysis")
    print(f"  • {len(resources)} Resources with ethical knowledge")
    print(f"  • {len(prompts)} Prompts for guided reasoning")
    print(f"  • {len(ETHICAL_FRAMEWORKS)} Ethical frameworks implemented")
    print(f"  • {len(AI_ETHICS_GUIDELINES)} AI ethics principles")
    print("\nThe server is ready to use!")


if __name__ == "__main__":
    asyncio.run(test_server())
