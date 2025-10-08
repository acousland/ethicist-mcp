# Quick Start Guide

Get started with the Ethicist MCP Server in minutes!

## Installation

```bash
# Clone the repository
git clone https://github.com/acousland/ethicist-mcp.git
cd ethicist-mcp

# Create an isolated environment using uv.lock
uv sync --python 3.10
```

## Verify Installation

```bash
# Run the demo
uv run python demo.py

# Or run tests
uv run python test_server.py
```

## Configure OpenAI Access

Set your credentials before running the tools:

```bash
export OPENAI_API_KEY="sk-..."
# optional: export OPENAI_MODEL="gpt-4o-mini"
```

## Basic Usage

### 1. Run the Server (Stdio Transport)

```bash
uv run ethicist-mcp
```

Or:

```bash
uv run python -m ethicist_mcp.server
```

### 2. Use in Claude Desktop

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ethicist": {
      "command": "uv",
      "args": ["run", "python", "-m", "ethicist_mcp.server"]
    }
  }
}
```

Then restart Claude Desktop and you'll have access to ethical analysis tools!

### 3. Try the Tools

Once connected to an MCP client, try these commands:

**Analyse an ethical scenario:**
```
Please analyse this ethical scenario using the ethicist server:
"Should we deploy facial recognition in our office building?"
```

**Evaluate an AI system:**
```
Use the ethicist server to evaluate our resume screening AI
```

**Check for bias:**
```
Check for bias in our training data using the ethicist server
```

## Examples

See [EXAMPLES.md](EXAMPLES.md) for detailed usage examples of all tools.

## Next Steps

- Read the [README.md](README.md) for full documentation
- Explore [EXAMPLES.md](EXAMPLES.md) for practical use cases
- Check [CONFIGURATION.md](CONFIGURATION.md) for advanced setup
- Run `uv run python demo.py` to see all features in action

## Troubleshooting

**Issue**: `ethicist-mcp` command not found

**Solution**: Use `uv run ethicist-mcp` (preferred) or ensure the editable install is on your PATH:
```bash
uv sync --python 3.10
uv run ethicist-mcp
# or (pip fallback)
pip install -e .
```

**Issue**: Import errors

**Solution**: Recreate the environment:
```bash
uv sync --python 3.10
# or (pip fallback)
pip install -r requirements.txt
```

## Support

- GitHub Issues: https://github.com/acousland/ethicist-mcp/issues
- Documentation: See README.md and EXAMPLES.md

Happy ethical AI building! 🎯
