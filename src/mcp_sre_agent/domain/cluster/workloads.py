"""Domain models for workload-focused cluster MCP tools."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


WorkloadTargetType = Literal["service", "deployment", "statefulset", "daemonset"]
ControllerTargetType = Literal["deployment", "statefulset", "daemonset"]


class WorkloadCondition(BaseModel):
    """A normalized workload condition."""

    type: str
    status: str
    reason: str | None = None
    message: str | None = None


class WorkloadStatusResult(BaseModel):
    """Reduced status summary for a controller workload."""

    cluster: str | None = None
    namespace: str
    target_type: ControllerTargetType
    target_name: str
    desired_replicas: int | None = None
    ready_replicas: int | None = None
    updated_replicas: int | None = None
    available_replicas: int | None = None
    observed_generation: int | None = None
    selector: dict[str, str] = Field(default_factory=dict)
    conditions: list[WorkloadCondition] = Field(default_factory=list)


class PodHealthSummary(BaseModel):
    """A reduced health-oriented representation of a pod."""

    name: str
    namespace: str
    phase: str | None = None
    ready: bool = False
    restart_count: int = 0
    reason: str | None = None
    node_name: str | None = None
    pod_ip: str | None = None


class WorkloadPodsResult(BaseModel):
    """Pods attached to one workload or service target."""

    cluster: str | None = None
    namespace: str
    target_type: WorkloadTargetType
    target_name: str
    count: int
    selector: dict[str, str] = Field(default_factory=dict)
    pods: list[PodHealthSummary] = Field(default_factory=list)


class WorkloadMatch(BaseModel):
    """A reduced discovery result for a service or workload target."""

    namespace: str
    target_type: WorkloadTargetType
    target_name: str


class FindWorkloadsResult(BaseModel):
    """Discovery results for workload and service targets matching a query."""

    cluster: str | None = None
    query: str
    namespace: str | None = None
    count: int
    matches: list[WorkloadMatch] = Field(default_factory=list)


class WorkloadHealthResult(BaseModel):
    """Aggregated health result for one workload or service target."""

    cluster: str | None = None
    namespace: str
    target_type: WorkloadTargetType
    target_name: str
    overall_status: Literal["healthy", "degraded", "unhealthy", "unknown"]
    summary: str
    total_pods: int
    unhealthy_pods: int
    desired_replicas: int | None = None
    ready_replicas: int | None = None
    issues: list[str] = Field(default_factory=list)
    pods: list[PodHealthSummary] = Field(default_factory=list)
    status: WorkloadStatusResult | None = None
