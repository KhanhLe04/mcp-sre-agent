"""Kubernetes pod operations."""

from __future__ import annotations

from kubernetes import client
from kubernetes.client.exceptions import ApiException

from mcp_sre_agent.adapters.kubernetes.client import build_core_v1_api
from mcp_sre_agent.adapters.kubernetes.nodes import KubernetesAccessError
from mcp_sre_agent.app.config import get_settings
from mcp_sre_agent.domain.cluster import ListNamespacePodsResult, PodSummary
from mcp_sre_agent.domain.common import NamespaceScope


class KubernetesPodService:
    """Service layer for namespace-scoped pod reads."""

    def __init__(self, api: client.CoreV1Api | None = None) -> None:
        self._api = api or build_core_v1_api()
        self._settings = get_settings()

    def list_namespace_pods(self, scope: NamespaceScope) -> ListNamespacePodsResult:
        """Return a reduced summary of pods in one namespace."""

        try:
            items = self._api.list_namespaced_pod(namespace=scope.namespace).items
        except ApiException as exc:
            raise KubernetesAccessError(
                f"Kubernetes API request failed while listing pods in namespace '{scope.namespace}'."
            ) from exc

        pods = [
            PodSummary(
                name=pod.metadata.name,
                namespace=pod.metadata.namespace,
                phase=getattr(pod.status, "phase", None),
                node_name=getattr(pod.spec, "node_name", None),
                pod_ip=getattr(pod.status, "pod_ip", None),
            )
            for pod in items
        ]
        pods.sort(key=lambda item: item.name)

        return ListNamespacePodsResult(
            cluster=self._settings.kube_context,
            namespace=scope.namespace,
            count=len(pods),
            pods=pods,
        )
