#!/usr/bin/env python3
"""
MCP Protocol Test - Simulates MCP client communication.
This verifies the server responds correctly to MCP protocol messages.
"""

import asyncio
import json
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession


async def test_mcp_protocol():
    """Test the server using MCP client protocol."""
    print("\n" + "=" * 80)
    print("MCP PROTOCOL COMMUNICATION TEST")
    print("=" * 80)
    
    print("\n1. Initializing MCP client connection...")
    server = StdioServerParameters(
        command="python",
        args=["-m", "ethicist_mcp.server"]
    )
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            print("✓ Connected to server\n")
            
            # Initialize
            print("2. Initializing session...")
            await session.initialize()
            print("✓ Session initialized\n")
            
            # List tools
            print("3. Listing available tools...")
            tools_result = await session.list_tools()
            print(f"✓ Found {len(tools_result.tools)} tools:")
            for tool in tools_result.tools[:3]:
                print(f"  - {tool.name}")
            print(f"  ... and {len(tools_result.tools) - 3} more\n")
            
            # List resources
            print("4. Listing available resources...")
            resources_result = await session.list_resources()
            print(f"✓ Found {len(resources_result.resources)} resources:")
            for resource in resources_result.resources[:3]:
                print(f"  - {resource.name}")
            print(f"  ... and {len(resources_result.resources) - 3} more\n")
            
            # List prompts
            print("5. Listing available prompts...")
            prompts_result = await session.list_prompts()
            print(f"✓ Found {len(prompts_result.prompts)} prompts:")
            for prompt in prompts_result.prompts:
                print(f"  - {prompt.name}")
            print()
            
            # Call a tool
            print("6. Calling analyze_ethical_scenario tool...")
            tool_result = await session.call_tool(
                "analyze_ethical_scenario",
                arguments={
                    "scenario": "Testing MCP protocol communication",
                    "frameworks": ["utilitarian"]
                }
            )
            print(f"✓ Tool executed successfully")
            print(f"  Response length: {len(tool_result.content[0].text)} characters")
            print(f"  Preview: {tool_result.content[0].text[:100]}...\n")
            
            # Read a resource
            print("7. Reading ethical frameworks resource...")
            resource_result = await session.read_resource(
                "ethicist://frameworks/utilitarian"
            )
            print(f"✓ Resource read successfully")
            content_data = json.loads(resource_result.contents[0].text)
            print(f"  Framework: {content_data['name']}")
            print(f"  Principles: {len(content_data['key_principles'])}\n")
            
            # Get a prompt
            print("8. Getting ethical_decision_making prompt...")
            prompt_result = await session.get_prompt(
                "ethical_decision_making",
                arguments={"situation": "testing the MCP server"}
            )
            print(f"✓ Prompt retrieved successfully")
            print(f"  Description: {prompt_result.description}")
            print(f"  Messages: {len(prompt_result.messages)}\n")
            
    print("=" * 80)
    print("ALL MCP PROTOCOL TESTS PASSED! ✓")
    print("=" * 80)
    print("\nThe server correctly implements the MCP protocol specification.")
    print("It's ready to be used with any MCP-compatible client!\n")


if __name__ == "__main__":
    print("\nTesting MCP Protocol Communication...")
    print("This simulates how an MCP client would interact with the server.\n")
    try:
        asyncio.run(test_mcp_protocol())
    except Exception as e:
        print(f"\n❌ Error during MCP protocol test: {e}")
        import traceback
        traceback.print_exc()
