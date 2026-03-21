"""Cluster MCP tools related to workload status and health."""

from __future__ import annotations

from functools import lru_cache

from mcp.server.fastmcp import FastMCP

from mcp_sre_agent.adapters.kubernetes import KubernetesAccessError, KubernetesWorkloadService
from mcp_sre_agent.domain.cluster import (
    FindWorkloadsResult,
    PodHealthSummary,
    WorkloadHealthResult,
    WorkloadPodsResult,
    WorkloadStatusResult,
    WorkloadTargetType,
)
from mcp_sre_agent.servers.tooling import (
    raise_kubernetes_error,
    validate_limit,
    validate_namespace,
    validate_required_string,
)


@lru_cache(maxsize=1)
def get_workload_service() -> KubernetesWorkloadService:
    """Return the singleton workload service."""

    return KubernetesWorkloadService()


def register_workload_tools(server: FastMCP) -> None:
    """Register workload-related tools on the cluster server."""

    @server.tool(
        name="find_workloads",
        description=(
            "Find Kubernetes services, deployments, statefulsets, or daemonsets by partial name. "
            "Use when the user says a workload name like 'traefik', 'ingress', or 'checkout' but "
            "does not know the exact target type or namespace yet. Returns discovery matches that "
            "can be passed to list_workload_pods or get_workload_health."
        ),
    )
    def find_workloads(
        query: str,
        namespace: str | None = None,
        limit: int = 20,
    ) -> FindWorkloadsResult:
        search_query = validate_required_string(query, field_name="query")
        search_limit = validate_limit(limit, field_name="limit")
        validated_namespace = validate_namespace(namespace).namespace if namespace is not None else None
        try:
            return get_workload_service().find_workloads(
                search_query,
                namespace=validated_namespace,
                limit=search_limit,
            )
        except KubernetesAccessError as exc:
            raise_kubernetes_error(exc)

    @server.tool(
        name="get_pod_status",
        description=(
            "Get one pod health summary by namespace and pod name. Use for questions like "
            "'why is this pod failing', 'is this pod ready', or 'how many restarts does this pod have'."
        ),
    )
    def get_pod_status(namespace: str, pod_name: str) -> PodHealthSummary:
        scope = validate_namespace(namespace)
        name = validate_required_string(pod_name, field_name="pod_name")
        try:
            return get_workload_service().get_pod_status(scope.namespace, name)
        except KubernetesAccessError as exc:
            raise_kubernetes_error(exc)

    @server.tool(
        name="get_deployment_status",
        description=(
            "Get one deployment rollout/status summary by namespace and deployment name. Use when the "
            "user asks whether a deployment is up, ready, or fully rolled out."
        ),
    )
    def get_deployment_status(namespace: str, deployment_name: str) -> WorkloadStatusResult:
        scope = validate_namespace(namespace)
        name = validate_required_string(deployment_name, field_name="deployment_name")
        try:
            return get_workload_service().get_deployment_status(scope.namespace, name)
        except KubernetesAccessError as exc:
            raise_kubernetes_error(exc)

    @server.tool(
        name="get_statefulset_status",
        description=(
            "Get one statefulset rollout/status summary by namespace and statefulset name. Use when the "
            "user asks whether a stateful workload is ready or fully rolled out."
        ),
    )
    def get_statefulset_status(namespace: str, statefulset_name: str) -> WorkloadStatusResult:
        scope = validate_namespace(namespace)
        name = validate_required_string(statefulset_name, field_name="statefulset_name")
        try:
            return get_workload_service().get_statefulset_status(scope.namespace, name)
        except KubernetesAccessError as exc:
            raise_kubernetes_error(exc)

    @server.tool(
        name="get_daemonset_status",
        description=(
            "Get one daemonset rollout/status summary by namespace and daemonset name. Use when the "
            "user asks whether an agent or node-wide workload is healthy on all nodes."
        ),
    )
    def get_daemonset_status(namespace: str, daemonset_name: str) -> WorkloadStatusResult:
        scope = validate_namespace(namespace)
        name = validate_required_string(daemonset_name, field_name="daemonset_name")
        try:
            return get_workload_service().get_daemonset_status(scope.namespace, name)
        except KubernetesAccessError as exc:
            raise_kubernetes_error(exc)

    @server.tool(
        name="list_workload_pods",
        description=(
            "List pods behind a Kubernetes service, deployment, statefulset, or daemonset in one "
            "namespace. Use for questions like 'show me the pods for Traefik', 'what pods back this "
            "service', or 'which workload pods are failing'."
        ),
    )
    def list_workload_pods(
        target_type: WorkloadTargetType,
        namespace: str,
        target_name: str,
    ) -> WorkloadPodsResult:
        scope = validate_namespace(namespace)
        name = validate_required_string(target_name, field_name="target_name")
        try:
            return get_workload_service().list_workload_pods(target_type, scope.namespace, name)
        except KubernetesAccessError as exc:
            raise_kubernetes_error(exc)

    @server.tool(
        name="get_workload_health",
        description=(
            "Check whether a Kubernetes service, deployment, statefulset, or daemonset is healthy by "
            "aggregating pod readiness and controller status. Use for questions like 'is this service "
            "healthy', 'are all pods ready', 'is rollout healthy', or 'why is this workload degraded'."
        ),
    )
    def get_workload_health(
        target_type: WorkloadTargetType,
        namespace: str,
        target_name: str,
    ) -> WorkloadHealthResult:
        scope = validate_namespace(namespace)
        name = validate_required_string(target_name, field_name="target_name")
        try:
            return get_workload_service().get_workload_health(target_type, scope.namespace, name)
        except KubernetesAccessError as exc:
            raise_kubernetes_error(exc)
