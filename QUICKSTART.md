# Quick Start Guide

Get started with the Ethicist MCP Server in minutes!

## Installation

```bash
# Clone the repository
git clone https://github.com/acousland/ethicist-mcp.git
cd ethicist-mcp

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Verify Installation

```bash
# Run the demo
python demo.py

# Or run tests
python test_server.py
```

## Basic Usage

### 1. Run the Server (Stdio Transport)

```bash
ethicist-mcp
```

Or:

```bash
python -m ethicist_mcp.server
```

### 2. Use in Claude Desktop

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

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

Then restart Claude Desktop and you'll have access to ethical analysis tools!

### 3. Try the Tools

Once connected to an MCP client, try these commands:

**Analyze an ethical scenario:**
```
Please analyze this ethical scenario using the ethicist server:
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
- Run `python demo.py` to see all features in action

## Troubleshooting

**Issue**: `ethicist-mcp` command not found

**Solution**: Make sure the package is installed and your PATH includes the pip bin directory:
```bash
pip install -e .
# or
python -m ethicist_mcp.server
```

**Issue**: Import errors

**Solution**: Install all dependencies:
```bash
pip install -r requirements.txt
```

## Support

- GitHub Issues: https://github.com/acousland/ethicist-mcp/issues
- Documentation: See README.md and EXAMPLES.md

Happy ethical AI building! 🎯
