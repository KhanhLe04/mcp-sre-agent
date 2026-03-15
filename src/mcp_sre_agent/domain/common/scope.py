"""Shared scope models for infrastructure and investigation requests."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ClusterScope(BaseModel):
    """The minimum scope needed to identify a cluster target."""

    cluster: str | None = None


class NamespaceScope(ClusterScope):
    """A cluster scope narrowed to one namespace."""

    namespace: str = Field(min_length=1)


class WorkloadScope(NamespaceScope):
    """A namespace scope narrowed to one workload."""

    kind: str = Field(min_length=1)
    name: str = Field(min_length=1)
