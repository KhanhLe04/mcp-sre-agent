"""Cluster MCP tools related to nodes."""

from __future__ import annotations

from functools import lru_cache

from mcp.server.fastmcp import FastMCP

from mcp_sre_agent.adapters.kubernetes import KubernetesAccessError, KubernetesClusterService
from mcp_sre_agent.domain.common import ErrorCategory
from mcp_sre_agent.domain.cluster import ListNodesResult
from mcp_sre_agent.servers.errors import raise_tool_error


@lru_cache(maxsize=1)
def get_cluster_service() -> KubernetesClusterService:
    """Return the singleton cluster service."""

    return KubernetesClusterService()


def register_node_tools(server: FastMCP) -> None:
    """Register node-related tools on the cluster server."""

    @server.tool(
        name="list_nodes",
        description="List available Kubernetes nodes with readiness and basic runtime details.",
    )
    def list_nodes() -> ListNodesResult:
        try:
            return get_cluster_service().list_nodes()
        except KubernetesAccessError as exc:
            raise_tool_error(
                category=ErrorCategory.UPSTREAM_UNAVAILABLE,
                message=str(exc),
                retryable=True,
            )

    @server.tool(
        name="get_node",
        description="Get one Kubernetes node by name with readiness and runtime details.",
    )
    def get_node(name: str):
        try:
            return get_cluster_service().get_node(name)
        except KubernetesAccessError as exc:
            category = (
                ErrorCategory.NOT_FOUND
                if "was not found" in str(exc)
                else ErrorCategory.UPSTREAM_UNAVAILABLE
            )
            raise_tool_error(
                category=category,
                message=str(exc),
                retryable=category == ErrorCategory.UPSTREAM_UNAVAILABLE,
            )
