"""Kubernetes resource creation operations."""

from __future__ import annotations

from kubernetes import client
from kubernetes.client.exceptions import ApiException

from mcp_sre_agent.adapters.kubernetes.client import build_core_v1_api, build_apps_v1_api
from mcp_sre_agent.adapters.kubernetes.nodes import KubernetesAccessError
from mcp_sre_agent.app.config import get_settings
from mcp_sre_agent.domain.cluster import (
    ContainerSpec,
    CreateDeploymentRequest,
    CreatePodRequest,
    CreationResult,
    PodSpec,
    DeploymentSpec,
)


class KubernetesCreationService:
    """Service layer for creating Kubernetes resources."""

    def __init__(
        self,
        *,
        core_api: client.CoreV1Api | None = None,
        apps_api: client.AppsV1Api | None = None,
    ) -> None:
        self._core_api = core_api or build_core_v1_api()
        self._apps_api = apps_api or build_apps_v1_api()
        self._settings = get_settings()

    def create_pod(self, request: CreatePodRequest) -> CreationResult:
        """Create a pod in the specified namespace."""

        # Build container specs
        k8s_containers = [
            client.V1Container(
                name=c.name,
                image=c.image,
                command=c.command,
                args=c.args,
                ports=[client.V1ContainerPort(container_port=c.port)] if c.port else None,
                env=[client.V1EnvVar(name=k, value=v) for k, v in c.env.items()] if c.env else None,
                resources=self._build_resources(c.resources) if c.resources else None,
            )
            for c in request.containers
        ]

        # Build pod spec
        pod_spec = client.V1PodSpec(
            service_account_name=request.pod_spec.service_account_name if request.pod_spec else None,
            node_selector=request.pod_spec.node_selector if request.pod_spec else None,
            affinity=self._build_affinity(request.pod_spec.affinity) if request.pod_spec else None,
            tolerations=[client.V1Toleration(**t) for t in request.pod_spec.tolerations] if request.pod_spec and request.pod_spec.tolerations else None,
            restart_policy=request.pod_spec.restart_policy if request.pod_spec else "Always",
            priority_class_name=request.pod_spec.priority_class_name if request.pod_spec else None,
            containers=k8s_containers,
        )

        # Build pod metadata
        metadata = client.V1ObjectMeta(
            name=request.name,
            namespace=request.namespace,
            labels=request.labels,
            annotations=request.annotations,
        )

        # Build pod object
        pod = client.V1Pod(
            api_version="v1",
            kind="Pod",
            metadata=metadata,
            spec=pod_spec,
        )

        try:
            self._core_api.create_namespaced_pod(
                namespace=request.namespace,
                body=pod,
            )
        except ApiException as exc:
            raise KubernetesAccessError(
                f"Failed to create pod '{request.name}' in namespace '{request.namespace}': {exc.reason}"
            ) from exc

        return CreationResult(
            name=request.name,
            namespace=request.namespace,
            resource_type="pod",
            success=True,
            message=f"Pod '{request.name}' created successfully in namespace '{request.namespace}'",
        )

    def create_deployment(self, request: CreateDeploymentRequest) -> CreationResult:
        """Create a deployment in the specified namespace."""

        # Build container specs
        k8s_containers = [
            client.V1Container(
                name=c.name,
                image=c.image,
                command=c.command,
                args=c.args,
                ports=[client.V1ContainerPort(container_port=c.port)] if c.port else None,
                env=[client.V1EnvVar(name=k, value=v) for k, v in c.env.items()] if c.env else None,
                resources=self._build_resources(c.resources) if c.resources else None,
            )
            for c in request.containers
        ]

        # Build pod template spec
        pod_spec = client.V1PodSpec(
            service_account_name=request.pod_spec.service_account_name if request.pod_spec else None,
            node_selector=request.pod_spec.node_selector if request.pod_spec else None,
            affinity=self._build_affinity(request.pod_spec.affinity) if request.pod_spec else None,
            tolerations=[client.V1Toleration(**t) for t in request.pod_spec.tolerations] if request.pod_spec and request.pod_spec.tolerations else None,
            restart_policy=request.pod_spec.restart_policy if request.pod_spec else "Always",
            priority_class_name=request.pod_spec.priority_class_name if request.pod_spec else None,
            containers=k8s_containers,
        )

        pod_template_labels = self._build_workload_labels(request.name, request.labels)
        pod_template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(
                labels=pod_template_labels,
                annotations=request.annotations,
            ),
            spec=pod_spec,
        )

        # Build deployment spec
        deployment_spec = client.V1DeploymentSpec(
            replicas=request.deployment_spec.replicas if request.deployment_spec else 1,
            min_ready_seconds=request.deployment_spec.min_ready_seconds if request.deployment_spec else 0,
            progress_deadline_seconds=request.deployment_spec.progress_deadline_seconds if request.deployment_spec else None,
            revision_history_limit=request.deployment_spec.revision_history_limit if request.deployment_spec else None,
            strategy=self._build_deployment_strategy(request.deployment_spec) if request.deployment_spec else None,
            selector=client.V1LabelSelector(
                match_labels={"app": request.name},
            ),
            template=pod_template,
        )

        # Build deployment metadata
        metadata = client.V1ObjectMeta(
            name=request.name,
            namespace=request.namespace,
            labels=pod_template_labels,
            annotations=request.annotations,
        )

        # Build deployment object
        deployment = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=metadata,
            spec=deployment_spec,
        )

        try:
            self._apps_api.create_namespaced_deployment(
                namespace=request.namespace,
                body=deployment,
            )
        except ApiException as exc:
            raise KubernetesAccessError(
                f"Failed to create deployment '{request.name}' in namespace '{request.namespace}': {exc.reason}"
            ) from exc

        return CreationResult(
            name=request.name,
            namespace=request.namespace,
            resource_type="deployment",
            success=True,
            message=f"Deployment '{request.name}' created successfully in namespace '{request.namespace}'",
        )

    def _build_resources(self, resources: dict[str, str]) -> client.V1ResourceRequirements:
        """Build Kubernetes resource requirements from dict."""
        requests = {}
        limits = {}
        for key, value in resources.items():
            if key.startswith("requests_"):
                requests[key.replace("requests_", "")] = value
            elif key.startswith("limits_"):
                limits[key.replace("limits_", "")] = value
            else:
                # Assume it's both if not prefixed
                requests[key] = value
                limits[key] = value
        return client.V1ResourceRequirements(
            requests=requests if requests else None,
            limits=limits if limits else None,
        )

    def _build_affinity(self, affinity: dict | None) -> client.V1Affinity | None:
        """Build Kubernetes affinity from dict."""
        if not affinity:
            return None
        return client.V1Affinity(**affinity)

    def _build_workload_labels(
        self,
        name: str,
        labels: dict[str, str] | None,
    ) -> dict[str, str]:
        """Build stable workload labels and ensure the selector label exists."""

        merged = dict(labels or {})
        merged["app"] = name
        return merged

    def _build_deployment_strategy(
        self, deployment_spec: DeploymentSpec
    ) -> client.V1DeploymentStrategy | None:
        """Build deployment strategy from spec."""
        if deployment_spec.strategy != "RollingUpdate":
            return client.V1DeploymentStrategy(type=deployment_spec.strategy)

        rolling_update = None
        if deployment_spec.rolling_update_max_surge or deployment_spec.rolling_update_max_unavailable:
            rolling_update = client.V1RollingUpdateDeployment(
                max_surge=deployment_spec.rolling_update_max_surge,
                max_unavailable=deployment_spec.rolling_update_max_unavailable,
            )

        return client.V1DeploymentStrategy(
            type=deployment_spec.strategy,
            rolling_update=rolling_update,
        )
