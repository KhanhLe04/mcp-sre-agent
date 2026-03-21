"""Cluster MCP tools related to pods."""

from __future__ import annotations

from functools import lru_cache

from mcp.server.fastmcp import FastMCP

from mcp_sre_agent.adapters.kubernetes import KubernetesAccessError, KubernetesPodService
from mcp_sre_agent.domain.cluster import ListNamespacePodsResult
from mcp_sre_agent.servers.tooling import raise_kubernetes_error, validate_namespace


@lru_cache(maxsize=1)
def get_pod_service() -> KubernetesPodService:
    """Return the singleton pod service."""

    return KubernetesPodService()


def register_pod_tools(server: FastMCP) -> None:
    """Register pod-related tools on the cluster server."""

    @server.tool(
        name="list_namespace_pods",
        description=(
            "List pods in one namespace with basic status details. Use when the user asks to show all "
            "pods in a namespace, inspect namespace-wide pod state, or quickly scan for failing pods."
        ),
    )
    def list_namespace_pods(namespace: str) -> ListNamespacePodsResult:
        scope = validate_namespace(namespace)
        try:
            return get_pod_service().list_namespace_pods(scope)
        except KubernetesAccessError as exc:
            raise_kubernetes_error(exc)
