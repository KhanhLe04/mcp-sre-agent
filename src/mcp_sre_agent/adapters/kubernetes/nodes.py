"""Kubernetes node operations."""

from __future__ import annotations

from kubernetes import client
from kubernetes.client.exceptions import ApiException

from mcp_sre_agent.adapters.kubernetes.client import build_core_v1_api
from mcp_sre_agent.app.config import get_settings
from mcp_sre_agent.domain.cluster import ListNodesResult, NodeSummary


class KubernetesAccessError(RuntimeError):
    """Raised when a Kubernetes API request fails and details should stay sanitized."""


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

    def get_node(self, name: str) -> NodeSummary:
        """Return a reduced summary for one node."""

        try:
            node = self._api.read_node(name=name)
        except ApiException as exc:
            if exc.status == 404:
                raise KubernetesAccessError(f"Kubernetes node '{name}' was not found.") from exc
            raise KubernetesAccessError(
                f"Kubernetes API request failed while fetching node '{name}'."
            ) from exc

        return NodeSummary(
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
