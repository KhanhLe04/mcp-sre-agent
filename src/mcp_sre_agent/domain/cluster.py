"""Domain models for cluster-focused MCP tools."""

from __future__ import annotations

from pydantic import BaseModel, Field


class NodeSummary(BaseModel):
    """A reduced representation of a Kubernetes node."""

    name: str
    ready: bool
    roles: list[str] = Field(default_factory=list)
    internal_ip: str | None = None
    kubelet_version: str | None = None
    os_image: str | None = None
    container_runtime: str | None = None


class ListNodesResult(BaseModel):
    """Structured response for the cluster list_nodes tool."""

    cluster: str | None = None
    count: int
    nodes: list[NodeSummary]
