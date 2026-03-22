"""Cluster MCP tools for creating pods and deployments."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from mcp_sre_agent.adapters.kubernetes import KubernetesAccessError, KubernetesCreationService
from mcp_sre_agent.domain.cluster import (
    ContainerSpec,
    CreateDeploymentRequest,
    CreatePodRequest,
    CreationResult,
    DeploymentSpec,
    PodSpec,
)
from mcp_sre_agent.servers.tooling import (
    raise_kubernetes_error,
    validate_namespace,
    validate_required_string,
)


def get_creation_service() -> KubernetesCreationService:
    """Return the singleton creation service."""

    return KubernetesCreationService()


def register_creation_tools(server: FastMCP) -> None:
    """Register creation tools on the cluster server."""

    @server.tool(
        name="create_pod",
        description=(
            "Create a pod with detailed specifications in a namespace. "
            "Use when the user asks to create a pod with specific requirements like: "
            "container image, commands, ports, environment variables, resources, labels, or pod-level settings. "
            "Example: 'Create a pod named test-pod with nginx:latest image, port 80, and 100m CPU limit'."
        ),
    )
    def create_pod(
        name: str,
        namespace: str | None = None,
        labels: dict[str, str] | None = None,
        annotations: dict[str, str] | None = None,
        containers: list[ContainerSpec] | None = None,
        pod_spec: PodSpec | None = None,
    ) -> CreationResult:
        """Create a pod with detailed specifications.

        Args:
            name: Pod name (required, must be unique within namespace)
            namespace: Namespace to create in (default: 'default')
            labels: Key-value pairs for pod labeling
            annotations: Key-value pairs for pod annotations
            containers: Typed container specifications. Use `port` for one port or
                `ports` for the legacy alternate input supported by `ContainerSpec`.
            pod_spec: Typed pod-level specifications.
        """
        validated_name = validate_required_string(name, field_name="name")
        validated_namespace = validate_namespace(namespace).namespace if namespace is not None else "default"

        if not containers:
            raise RuntimeError("At least one container specification is required")

        request = CreatePodRequest(
            name=validated_name,
            namespace=validated_namespace,
            labels=labels,
            annotations=annotations,
            containers=containers,
            pod_spec=pod_spec,
        )

        try:
            return get_creation_service().create_pod(request)
        except KubernetesAccessError as exc:
            raise_kubernetes_error(exc)

    @server.tool(
        name="create_deployment",
        description=(
            "Create a deployment with detailed specifications in a namespace. "
            "Use when the user asks to create a deployment with replica management, "
            "rollout strategy, or container specifications. "
            "Example: 'Create a deployment named web-app with 3 replicas, nginx:latest, port 80'."
        ),
    )
    def create_deployment(
        name: str,
        namespace: str | None = None,
        labels: dict[str, str] | None = None,
        annotations: dict[str, str] | None = None,
        containers: list[ContainerSpec] | None = None,
        pod_spec: PodSpec | None = None,
        deployment_spec: DeploymentSpec | None = None,
    ) -> CreationResult:
        """Create a deployment with detailed specifications.

        Args:
            name: Deployment name (required, must be unique within namespace)
            namespace: Namespace to create in (default: 'default')
            labels: Key-value pairs for deployment labeling
            annotations: Key-value pairs for deployment annotations
            containers: Typed container specifications. Use `port` for one port or
                `ports` for the legacy alternate input supported by `ContainerSpec`.
            pod_spec: Typed pod template specifications.
            deployment_spec: Typed deployment-level specifications.
        """
        validated_name = validate_required_string(name, field_name="name")
        validated_namespace = validate_namespace(namespace).namespace if namespace is not None else "default"

        if not containers:
            raise RuntimeError("At least one container specification is required")

        request = CreateDeploymentRequest(
            name=validated_name,
            namespace=validated_namespace,
            labels=labels,
            annotations=annotations,
            containers=containers,
            pod_spec=pod_spec,
            deployment_spec=deployment_spec,
        )

        try:
            return get_creation_service().create_deployment(request)
        except KubernetesAccessError as exc:
            raise_kubernetes_error(exc)
