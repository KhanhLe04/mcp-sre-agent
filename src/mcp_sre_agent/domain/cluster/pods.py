"""Domain models for cluster pod MCP tools."""

from __future__ import annotations

from pydantic import BaseModel


class PodSummary(BaseModel):
    """A reduced representation of a Kubernetes pod."""

    name: str
    namespace: str
    phase: str | None = None
    node_name: str | None = None
    pod_ip: str | None = None


class ListNamespacePodsResult(BaseModel):
    """Structured response for namespace-scoped pod listing."""

    cluster: str | None = None
    namespace: str
    count: int
    pods: list[PodSummary]
