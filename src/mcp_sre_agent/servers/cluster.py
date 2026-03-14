"""Cluster MCP server and its tool registrations."""

from __future__ import annotations

from functools import lru_cache

from mcp.server.fastmcp import FastMCP

from mcp_sre_agent.adapters.kubernetes import KubernetesAccessError, KubernetesClusterService
from mcp_sre_agent.app.config import get_settings
from mcp_sre_agent.domain.cluster import ListNodesResult


@lru_cache(maxsize=1)
def get_cluster_service() -> KubernetesClusterService:
    """Return the singleton cluster service."""

    return KubernetesClusterService()


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

    @server.tool(
        name="list_nodes",
        description="List available Kubernetes nodes with readiness and basic runtime details.",
    )
    def list_nodes() -> ListNodesResult:
        try:
            return get_cluster_service().list_nodes()
        except KubernetesAccessError as exc:
            raise RuntimeError(str(exc)) from exc

    return server
