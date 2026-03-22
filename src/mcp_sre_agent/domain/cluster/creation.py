"""Domain models for pod and deployment creation."""

from __future__ import annotations

from typing import Any
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ContainerPortSpec(BaseModel):
    """Typed container port input for creation tools."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    container_port: int = Field(
        alias="containerPort",
        ge=1,
        le=65535,
        description="Container port to expose",
    )


class ContainerSpec(BaseModel):
    """Specification for a container within a pod."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    name: str = Field(min_length=1, description="Container name")
    image: str = Field(min_length=1, description="Container image (e.g., nginx:latest)")
    command: list[str] | None = Field(
        default=None,
        description="Override container entrypoint command",
    )
    args: list[str] | None = Field(
        default=None,
        description="Arguments for the container command",
    )
    port: int | None = Field(
        default=None,
        ge=1,
        le=65535,
        description="Container port to expose",
    )
    ports: list[int | ContainerPortSpec] | None = Field(
        default=None,
        description="Optional alternate port input; the first port is used if present",
    )
    env: dict[str, str] | None = Field(
        default=None,
        description="Environment variables for the container",
    )
    resources: dict[str, str] | None = Field(
        default=None,
        description="Resource requests/limits (e.g., {'cpu': '100m', 'memory': '128Mi'})",
    )

    @model_validator(mode="after")
    def normalize_port(self) -> "ContainerSpec":
        """Normalize `ports` into the single `port` field used by adapters."""

        if self.port is not None:
            return self

        if not self.ports:
            return self

        first_port = self.ports[0]
        if isinstance(first_port, int):
            self.port = first_port
        elif isinstance(first_port, ContainerPortSpec):
            self.port = first_port.container_port

        return self


class PodSpec(BaseModel):
    """Pod specification details."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    service_account_name: str | None = Field(
        default=None,
        description="Service account to use for the pod",
    )
    node_selector: dict[str, str] | None = Field(
        default=None,
        description="Node selector labels",
    )
    affinity: dict[str, Any] | None = Field(
        default=None,
        description="Pod affinity/anti-affinity rules",
    )
    tolerations: list[dict[str, Any]] | None = Field(
        default=None,
        description="Tolerations for node taints",
    )
    restart_policy: Literal["Always", "OnFailure", "Never"] = Field(
        default="Always",
        description="Restart policy for the pod",
    )
    priority_class_name: str | None = Field(
        default=None,
        description="Priority class name for pod scheduling",
    )


class DeploymentSpec(BaseModel):
    """Deployment specification details."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    replicas: int = Field(default=1, ge=1, description="Number of pod replicas")
    min_ready_seconds: int = Field(default=0, ge=0, description="Seconds to wait after pod is ready")
    progress_deadline_seconds: int | None = Field(
        default=None,
        ge=1,
        description="Seconds to wait for deployment progress before timing out",
    )
    revision_history_limit: int | None = Field(
        default=None,
        ge=0,
        description="Number of old replica sets to retain",
    )
    strategy: Literal["RollingUpdate", "Recreate"] = Field(
        default="RollingUpdate",
        description="Deployment strategy",
    )
    rolling_update_max_surge: str | None = Field(
        default=None,
        description="Max surge during rolling update (e.g., '25%')",
    )
    rolling_update_max_unavailable: str | None = Field(
        default=None,
        description="Max unavailable during rolling update (e.g., '25%')",
    )


class CreatePodRequest(BaseModel):
    """Request to create a pod."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    name: str = Field(min_length=1, description="Pod name")
    namespace: str = Field(default="default", description="Namespace to create the pod in")
    labels: dict[str, str] | None = Field(
        default=None,
        description="Labels to apply to the pod",
    )
    annotations: dict[str, str] | None = Field(
        default=None,
        description="Annotations to apply to the pod",
    )
    containers: list[ContainerSpec] = Field(
        min_length=1,
        description="List of container specifications",
    )
    pod_spec: PodSpec | None = Field(
        default=None,
        description="Additional pod-level specifications",
    )


class CreateDeploymentRequest(BaseModel):
    """Request to create a deployment."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    name: str = Field(min_length=1, description="Deployment name")
    namespace: str = Field(default="default", description="Namespace to create the deployment in")
    labels: dict[str, str] | None = Field(
        default=None,
        description="Labels to apply to the deployment",
    )
    annotations: dict[str, str] | None = Field(
        default=None,
        description="Annotations to apply to the deployment",
    )
    containers: list[ContainerSpec] = Field(
        min_length=1,
        description="List of container specifications",
    )
    pod_spec: PodSpec | None = Field(
        default=None,
        description="Pod template specifications",
    )
    deployment_spec: DeploymentSpec | None = Field(
        default=None,
        description="Deployment-level specifications",
    )


class CreationResult(BaseModel):
    """Result of a resource creation operation."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    name: str
    namespace: str
    resource_type: str
    success: bool
    message: str
