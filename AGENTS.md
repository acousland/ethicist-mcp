# Repository Guidelines

## Project Structure & Module Organisation
The codebase centers on the `ethicist_mcp` package, which exposes the MCP server logic. `ethicist_mcp/server.py` implements the stdio entry point and tool/resource definitions, while `ethicist_mcp/http_server.py` wraps the same server for HTTP/SSE transport. Example workflows live in `demo.py` plus narrative guides in `README.md`, `QUICKSTART.md`, and `CONFIGURATION.md`. Integration tests and protocol smoke checks sit at the repo root (`test_server.py`, `test_mcp_protocol.py`). Packaging metadata and dependency manifests live in `pyproject.toml`, `uv.lock`, and (legacy) `requirements.txt`.

## Build, Test, and Development Commands
Install dependencies with uv (recommended):
```bash
uv sync --python 3.10
```
Run the stdio server locally via `uv run python -m ethicist_mcp.server`, or start the experimental HTTP endpoint with `uv run python -m ethicist_mcp.http_server 127.0.0.1 8080`. Use `uv run python demo.py` to exercise the tool surface, `uv run python test_server.py` for asynchronous smoke tests, and `uv run python test_mcp_protocol.py` to simulate an MCP client. Pytest is configured; targeted suites can be added under `tests/` and run with `uv run pytest`. If pip workflows are needed, install with `pip install -r requirements.txt && pip install -e .`.

All AI-driven tools require an OpenAI credential. Export `OPENAI_API_KEY` (and optionally `OPENAI_MODEL`) before launching the server or running integration tests that exercise the tools.

## Coding Style & Naming Conventions
Write Python 3.10+ code using four-space indentation, descriptive function names, and type hints matching the existing modules. Follow PEP 8 defaults for imports, docstrings, and line wrapping (≤88 chars). Tool identifiers, resource URIs, and prompt names stay lowercase_snake_case to align with the existing MCP schema. Include concise comments only where context is non-obvious, and keep loggers configured through the `logging` module.

## Testing Guidelines
Prefer async-aware tests (`pytest-asyncio` is available) and cover new tool behaviours with direct calls to the registered handlers. Name files `test_<feature>.py` and co-locate fixtures under `tests/`. When touching protocol flows, extend `test_mcp_protocol.py` or add pytest variants that spin up `ethicist_mcp.server`. Before submitting, run `uv run python test_server.py` plus any affected `uv run pytest` suites.

## Commit & Pull Request Guidelines
Commit messages follow short, imperative phrasing (“Add protocol tests”, “Fix entry point”). Group related changes together and document user-facing updates in the body when needed. Pull requests should summarise scope, call out new commands or config knobs, link to tracking issues, and include console output or screenshots when behaviour changes. Mention any security or deployment considerations up front to help review move quickly.

## Security & Configuration Tips
Respect the `LOG_LEVEL` environment variable when adjusting logging. Avoid hard-coding credentials or external endpoints; prefer configuration files referenced in `CONFIGURATION.md`. For HTTP mode, document any exposed ports in the PR description and ensure TLS or reverse-proxy guidance accompanies production-facing changes.
