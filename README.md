# Ethicist MCP Server

A full-featured Model Context Protocol (MCP) server for ethical AI analysis and guidance, built with Python and supporting Streamable HTTP transport.

## Overview

The Ethicist MCP Server provides comprehensive tools, resources, and prompts for ethical analysis of AI systems and decision-making. It implements the MCP specification with support for both stdio and HTTP transports, making it easy to integrate into various AI applications and workflows.

## Features

### 🛠️ Tools

The server provides five powerful ethical analysis tools:

1. **analyze_ethical_scenario** - Analyze ethical scenarios using multiple frameworks (Utilitarian, Deontological, Virtue Ethics, Ethics of Care)
2. **evaluate_ai_system** - Evaluate AI systems against comprehensive ethical guidelines
3. **check_bias** - Check for various types of bias in AI systems and data
4. **generate_ethical_guidelines** - Generate customized ethical guidelines for specific projects
5. **assess_transparency** - Assess transparency and explainability of AI systems

### 📚 Resources

Access structured ethical knowledge through URI-based resources:

- `ethicist://frameworks/all` - Complete database of ethical frameworks
- `ethicist://guidelines/ai-ethics` - Comprehensive AI ethics guidelines
- `ethicist://frameworks/utilitarian` - Utilitarian ethics details
- `ethicist://frameworks/deontological` - Deontological ethics details
- `ethicist://frameworks/virtue` - Virtue ethics details
- `ethicist://frameworks/care` - Ethics of care details

### 💭 Prompts

Structured prompts to guide ethical reasoning:

- **ethical_decision_making** - Structured decision-making process
- **stakeholder_analysis** - Comprehensive stakeholder analysis
- **ai_risk_assessment** - AI system risk assessment

## Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager
- [uv](https://docs.astral.sh/uv/) CLI (optional, recommended for environment management)

### Install with uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/acousland/ethicist-mcp.git
cd ethicist-mcp

# Create a virtual environment pinned by uv.lock
uv sync --python 3.10

# Activate the environment if you prefer using python directly
source .venv/bin/activate  # on macOS/Linux
# .venv\Scripts\activate   # on Windows PowerShell
```

Once synced you can execute any script with isolated dependencies:

```bash
uv run ethicist-mcp
uv run python -m ethicist_mcp.server
```

### Install from Source with pip

```bash
# Clone the repository
git clone https://github.com/acousland/ethicist-mcp.git
cd ethicist-mcp

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

### Install Dependencies Only

```bash
# Using uv
uv pip install mcp httpx pydantic

# Using pip
pip install mcp httpx pydantic
```

## Usage

### Running with Stdio Transport (Default)

The default transport uses standard input/output, suitable for MCP clients:

```bash
ethicist-mcp
```

Or run directly with Python:

```bash
python -m ethicist_mcp.server
```

### Running with HTTP Transport

For HTTP/SSE transport (requires additional setup):

```bash
python -m ethicist_mcp.http_server
```

Specify custom host and port:

```bash
python -m ethicist_mcp.http_server 127.0.0.1 8080
```

### Integration with MCP Clients

Add to your MCP client configuration (e.g., Claude Desktop):

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

If you have the package installed globally (e.g., via `pip install -e .`), you can alternatively configure it with the direct entry point:

```json
{
  "mcpServers": {
    "ethicist": {
      "command": "ethicist-mcp"
    }
  }
}
```

## Examples

### Analyzing an Ethical Scenario

```python
# Using the analyze_ethical_scenario tool
{
  "scenario": "A self-driving car must choose between hitting a pedestrian or swerving and potentially harming its passengers.",
  "frameworks": ["utilitarian", "deontological"]
}
```

### Evaluating an AI System

```python
# Using the evaluate_ai_system tool
{
  "system_description": "A resume screening AI that ranks job candidates",
  "use_case": "Automated recruitment for tech positions",
  "stakeholders": ["job applicants", "hiring managers", "HR department"]
}
```

### Checking for Bias

```python
# Using the check_bias tool
{
  "context": "Training data for a loan approval model contains historical lending decisions from the past 20 years",
  "bias_types": ["selection", "representation", "measurement"]
}
```

### Generating Ethical Guidelines

```python
# Using the generate_ethical_guidelines tool
{
  "project_type": "healthcare AI diagnostic system",
  "risk_level": "high",
  "regulations": ["HIPAA", "FDA", "GDPR"]
}
```

### Assessing Transparency

```python
# Using the assess_transparency tool
{
  "system_type": "neural network for credit scoring",
  "explanation_method": "SHAP values",
  "stakeholder_needs": ["loan applicants", "regulators", "bank executives"]
}
```

## Ethical Frameworks

The server incorporates four major ethical frameworks:

### Utilitarian Ethics
Focuses on maximizing overall happiness and well-being for the greatest number of people.

### Deontological Ethics
Emphasizes duties, rules, and moral obligations regardless of consequences.

### Virtue Ethics
Focuses on character development and cultivating moral virtues.

### Ethics of Care
Emphasizes relationships, empathy, and context-sensitive responses.

## AI Ethics Guidelines

The server evaluates AI systems against eight core ethical principles:

1. **Fairness** - Equitable treatment without bias
2. **Transparency** - Understandable and explainable decisions
3. **Accountability** - Clear responsibility for outcomes
4. **Privacy** - Protection of personal data and rights
5. **Safety** - Security, reliability, and harm prevention
6. **Human Autonomy** - Preservation of human agency
7. **Beneficence** - Benefit to humanity and well-being
8. **Sustainability** - Long-term environmental and social impacts

## Development

### Project Structure

```
ethicist-mcp/
├── ethicist_mcp/
│   ├── __init__.py
│   ├── server.py         # Main MCP server implementation
│   └── http_server.py    # HTTP transport implementation
├── tests/                # Test suite (to be added)
├── pyproject.toml        # Project configuration
├── requirements.txt      # Python dependencies
├── .gitignore           # Git ignore patterns
└── README.md            # This file
```

### Running Tests

```bash
pytest
```

### Code Quality

The project follows Python best practices and PEP 8 style guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or contributions, please use the GitHub issue tracker.

## Acknowledgments

Built with the [Model Context Protocol](https://modelcontextprotocol.io/) SDK and inspired by ethical AI principles from leading organizations and researchers in the field.
