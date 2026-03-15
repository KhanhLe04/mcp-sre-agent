"""Cluster MCP server construction."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from mcp_sre_agent.app.config import get_settings
from mcp_sre_agent.servers.cluster.tools_nodes import register_node_tools
from mcp_sre_agent.servers.cluster.tools_pods import register_pod_tools


def create_cluster_server() -> FastMCP:
    """Build the cluster MCP server."""

    settings = get_settings()
    server = FastMCP(
        "cluster",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level,
        sse_path=settings.sse_path,
        message_path=settings.message_path,
        streamable_http_path=settings.streamable_http_path,
    )
    register_node_tools(server)
    register_pod_tools(server)
    return server
