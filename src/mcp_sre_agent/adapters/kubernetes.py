"""Kubernetes adapter helpers for the cluster MCP server."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from kubernetes import client, config
from kubernetes.client.exceptions import ApiException
from kubernetes.config.config_exception import ConfigException

from mcp_sre_agent.app.config import get_settings
from mcp_sre_agent.domain.cluster import ListNodesResult, NodeSummary


class KubernetesConfigurationError(RuntimeError):
    """Raised when no Kubernetes configuration can be loaded."""


class KubernetesAccessError(RuntimeError):
    """Raised when a Kubernetes API request fails and details should stay sanitized."""


@dataclass(frozen=True)
class KubernetesConnectionInfo:
    """Sanitized information about how the adapter is configured to connect."""

    source: str
    kubeconfig_label: str
    context: str | None


def _mask_path(path: str | None) -> str:
    if not path:
        return "<default>"

    name = Path(path).name
    return f".../{name}" if name else "<default>"


def planned_connection_info() -> KubernetesConnectionInfo:
    """Return sanitized connection intent before loading any credentials."""

    settings = get_settings()
    return KubernetesConnectionInfo(
        source="kubeconfig-or-incluster",
        kubeconfig_label=_mask_path(settings.kubeconfig),
        context=settings.kube_context,
    )


def _node_roles(labels: dict[str, str] | None) -> list[str]:
    if not labels:
        return []

    roles = []
    for key in labels:
        if key.startswith("node-role.kubernetes.io/"):
            role = key.split("/", 1)[1] or "control-plane"
            roles.append(role)

    return sorted(set(roles))


def _is_ready(statuses: list[object] | None) -> bool:
    if not statuses:
        return False

    for condition in statuses:
        if getattr(condition, "type", None) == "Ready":
            return getattr(condition, "status", None) == "True"

    return False


def _internal_ip(addresses: list[object] | None) -> str | None:
    if not addresses:
        return None

    for address in addresses:
        if getattr(address, "type", None) == "InternalIP":
            return getattr(address, "address", None)

    return None


@lru_cache(maxsize=1)
def build_core_v1_api() -> client.CoreV1Api:
    """Create a configured CoreV1Api client."""

    settings = get_settings()

    try:
        config.load_kube_config(
            config_file=settings.kubeconfig,
            context=settings.kube_context,
        )
    except ConfigException:
        try:
            config.load_incluster_config()
        except ConfigException as exc:
            raise KubernetesConfigurationError(
                "Unable to load Kubernetes configuration from kubeconfig or in-cluster settings."
            ) from exc

    return client.CoreV1Api()


class KubernetesClusterService:
    """Service layer for cluster-oriented Kubernetes reads."""

    def __init__(self, api: client.CoreV1Api | None = None) -> None:
        self._api = api or build_core_v1_api()
        self._settings = get_settings()

    def list_nodes(self) -> ListNodesResult:
        """Return a reduced summary of every available node."""

        try:
            items = self._api.list_node().items
        except ApiException as exc:
            raise KubernetesAccessError(
                "Kubernetes API request failed while listing nodes."
            ) from exc
        nodes = [
            NodeSummary(
                name=node.metadata.name,
                ready=_is_ready(getattr(node.status, "conditions", None)),
                roles=_node_roles(getattr(node.metadata, "labels", None)),
                internal_ip=_internal_ip(getattr(node.status, "addresses", None)),
                kubelet_version=getattr(node.status.node_info, "kubelet_version", None),
                os_image=getattr(node.status.node_info, "os_image", None),
                container_runtime=getattr(
                    node.status.node_info,
                    "container_runtime_version",
                    None,
                ),
            )
            for node in items
        ]

        nodes.sort(key=lambda item: item.name)

        return ListNodesResult(
            cluster=self._settings.kube_context,
            count=len(nodes),
            nodes=nodes,
        )
