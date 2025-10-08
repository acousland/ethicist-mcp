#!/usr/bin/env python3
"""
HTTP Transport implementation for Ethicist MCP Server.

This module provides Streamable HTTP transport support for the MCP server,
allowing it to be accessed via HTTP/HTTPS protocols.
"""

import asyncio
import json
import logging
from typing import Any
from contextlib import asynccontextmanager

try:
    from mcp.server.sse import sse_server
    SSE_AVAILABLE = True
except ImportError:
    SSE_AVAILABLE = False
    
from ethicist_mcp.server import app

logger = logging.getLogger("ethicist-mcp-http")


async def run_http_server(host: str = "0.0.0.0", port: int = 8000):
    """
    Run the MCP server with HTTP transport using Server-Sent Events (SSE).
    
    Args:
        host: Host address to bind to (default: 0.0.0.0)
        port: Port to listen on (default: 8000)
    """
    if not SSE_AVAILABLE:
        logger.error("SSE transport not available. Please install mcp with SSE support.")
        logger.info("You can run the server with stdio transport instead using: ethicist-mcp")
        return
    
    logger.info(f"Starting Ethicist MCP Server on http://{host}:{port}")
    logger.info("Server-Sent Events (SSE) transport enabled")
    
    try:
        async with sse_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"Error running HTTP server: {e}")
        raise


def main():
    """Entry point for HTTP server."""
    import sys
    
    host = sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    
    asyncio.run(run_http_server(host, port))


if __name__ == "__main__":
    main()
