"""Cluster MCP tools related to nodes."""

from __future__ import annotations

from functools import lru_cache

from mcp.server.fastmcp import FastMCP

from mcp_sre_agent.adapters.kubernetes import KubernetesAccessError, KubernetesClusterService
from mcp_sre_agent.domain.cluster import ListNodesResult
from mcp_sre_agent.servers.tooling import raise_kubernetes_error, validate_required_string


@lru_cache(maxsize=1)
def get_cluster_service() -> KubernetesClusterService:
    """Return the singleton cluster service."""

    return KubernetesClusterService()


def register_node_tools(server: FastMCP) -> None:
    """Register node-related tools on the cluster server."""

    @server.tool(
        name="list_nodes",
        description=(
            "List Kubernetes nodes with readiness and basic runtime details. Use when the user asks "
            "whether nodes are ready, how many nodes exist, or which nodes are available."
        ),
    )
    def list_nodes() -> ListNodesResult:
        try:
            return get_cluster_service().list_nodes()
        except KubernetesAccessError as exc:
            raise_kubernetes_error(exc)

    @server.tool(
        name="get_node",
        description=(
            "Get one Kubernetes node by name with readiness and runtime details. Use for questions like "
            "'is this node ready' or 'show details for node worker-a'."
        ),
    )
    def get_node(name: str):
        node_name = validate_required_string(name, field_name="name")
        try:
            return get_cluster_service().get_node(node_name)
        except KubernetesAccessError as exc:
            raise_kubernetes_error(exc)
