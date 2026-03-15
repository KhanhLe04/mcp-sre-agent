"""Cluster MCP tools related to pods."""

from __future__ import annotations

from functools import lru_cache

from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError

from mcp_sre_agent.adapters.kubernetes import KubernetesAccessError, KubernetesPodService
from mcp_sre_agent.domain.cluster import ListNamespacePodsResult
from mcp_sre_agent.domain.common import ErrorCategory, NamespaceScope
from mcp_sre_agent.servers.errors import raise_tool_error


@lru_cache(maxsize=1)
def get_pod_service() -> KubernetesPodService:
    """Return the singleton pod service."""

    return KubernetesPodService()


def register_pod_tools(server: FastMCP) -> None:
    """Register pod-related tools on the cluster server."""

    @server.tool(
        name="list_namespace_pods",
        description="List Kubernetes pods in one namespace with basic status details.",
    )
    def list_namespace_pods(namespace: str) -> ListNamespacePodsResult:
        try:
            scope = NamespaceScope(namespace=namespace)
            return get_pod_service().list_namespace_pods(scope)
        except ValidationError:
            raise_tool_error(
                category=ErrorCategory.INVALID_INPUT,
                message="namespace must be a non-empty string.",
            )
        except KubernetesAccessError as exc:
            raise_tool_error(
                category=ErrorCategory.UPSTREAM_UNAVAILABLE,
                message=str(exc),
                retryable=True,
            )
