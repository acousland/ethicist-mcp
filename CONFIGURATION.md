# Example MCP Client Configuration

This file provides example configurations for various MCP clients.

## Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ethicist": {
      "command": "ethicist-mcp"
    }
  }
}
```

Or using the full Python path:

```json
{
  "mcpServers": {
    "ethicist": {
      "command": "python",
      "args": ["-m", "ethicist_mcp.server"]
    }
  }
}
```

## Configuration File Location

### macOS
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### Windows
```
%APPDATA%\Claude\claude_desktop_config.json
```

### Linux
```
~/.config/Claude/claude_desktop_config.json
```

## Environment Variables

The server can be configured using environment variables:

- `LOG_LEVEL` - Set logging level (default: INFO)
  - Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

Example:
```bash
export LOG_LEVEL=DEBUG
ethicist-mcp
```

## HTTP Server Configuration

For running as an HTTP server (experimental):

```bash
# Default (0.0.0.0:8000)
python -m ethicist_mcp.http_server

# Custom host and port
python -m ethicist_mcp.http_server 127.0.0.1 3000
```

## Advanced Usage

### Using with Custom MCP Client

```python
import asyncio
from mcp.client import Client
from mcp.client.stdio import stdio_client

async def run_client():
    async with stdio_client("python", ["-m", "ethicist_mcp.server"]) as (read, write):
        async with Client(read, write) as client:
            # Initialize the client
            await client.initialize()
            
            # List available tools
            tools = await client.list_tools()
            print(f"Available tools: {[t.name for t in tools.tools]}")
            
            # Call a tool
            result = await client.call_tool(
                "analyze_ethical_scenario",
                {
                    "scenario": "Should AI be used in criminal sentencing?",
                    "frameworks": ["utilitarian", "deontological"]
                }
            )
            print(result)

if __name__ == "__main__":
    asyncio.run(run_client())
```
