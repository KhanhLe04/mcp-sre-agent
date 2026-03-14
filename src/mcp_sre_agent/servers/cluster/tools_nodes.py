"""Cluster MCP tools related to nodes."""

from __future__ import annotations

from functools import lru_cache

from mcp.server.fastmcp import FastMCP

from mcp_sre_agent.adapters.kubernetes import KubernetesAccessError, KubernetesClusterService
from mcp_sre_agent.domain.cluster import ListNodesResult


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
            raise RuntimeError(str(exc)) from exc
