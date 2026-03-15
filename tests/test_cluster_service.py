"""Unit tests for the cluster Kubernetes service."""

from __future__ import annotations

import unittest
from types import SimpleNamespace

from mcp_sre_agent.adapters.kubernetes import KubernetesClusterService, KubernetesPodService
from mcp_sre_agent.domain.common import NamespaceScope



def make_node(
    name: str,
    *,
    ready: bool,
    internal_ip: str,
    kubelet_version: str,
    role: str | None = None,
) -> SimpleNamespace:
    labels = {}
    if role:
        labels[f"node-role.kubernetes.io/{role}"] = ""

    return SimpleNamespace(
        metadata=SimpleNamespace(
            name=name,
            labels=labels,
        ),
        status=SimpleNamespace(
            conditions=[
                SimpleNamespace(type="Ready", status="True" if ready else "False"),
            ],
            addresses=[
                SimpleNamespace(type="InternalIP", address=internal_ip),
            ],
            node_info=SimpleNamespace(
                kubelet_version=kubelet_version,
                os_image="Ubuntu 24.04",
                container_runtime_version="containerd://1.7.0",
            ),
        ),
    )



def make_pod(
    name: str,
    *,
    namespace: str,
    phase: str,
    node_name: str,
    pod_ip: str,
) -> SimpleNamespace:
    return SimpleNamespace(
        metadata=SimpleNamespace(
            name=name,
            namespace=namespace,
        ),
        spec=SimpleNamespace(
            node_name=node_name,
        ),
        status=SimpleNamespace(
            phase=phase,
            pod_ip=pod_ip,
        ),
    )


class ClusterServiceTests(unittest.TestCase):
    def test_list_nodes_returns_sorted_reduced_summaries(self) -> None:
        api = SimpleNamespace(
            list_node=lambda: SimpleNamespace(
                items=[
                    make_node(
                        "worker-b",
                        ready=False,
                        internal_ip="10.0.0.12",
                        kubelet_version="v1.31.0",
                    ),
                    make_node(
                        "control-a",
                        ready=True,
                        internal_ip="10.0.0.10",
                        kubelet_version="v1.31.0",
                        role="control-plane",
                    ),
                ]
            )
        )

        result = KubernetesClusterService(api=api).list_nodes()

        self.assertEqual(result.count, 2)
        self.assertEqual([node.name for node in result.nodes], ["control-a", "worker-b"])
        self.assertTrue(result.nodes[0].ready)
        self.assertEqual(result.nodes[0].roles, ["control-plane"])
        self.assertEqual(result.nodes[1].internal_ip, "10.0.0.12")

    def test_get_node_returns_reduced_summary(self) -> None:
        api = SimpleNamespace(
            read_node=lambda name: make_node(
                name,
                ready=True,
                internal_ip="10.0.0.20",
                kubelet_version="v1.31.0",
                role="worker",
            )
        )

        result = KubernetesClusterService(api=api).get_node("worker-a")

        self.assertEqual(result.name, "worker-a")
        self.assertEqual(result.roles, ["worker"])
        self.assertEqual(result.internal_ip, "10.0.0.20")

    def test_list_namespace_pods_returns_sorted_reduced_summaries(self) -> None:
        api = SimpleNamespace(
            list_namespaced_pod=lambda namespace: SimpleNamespace(
                items=[
                    make_pod(
                        "api-b",
                        namespace=namespace,
                        phase="Running",
                        node_name="worker-b",
                        pod_ip="10.2.0.12",
                    ),
                    make_pod(
                        "api-a",
                        namespace=namespace,
                        phase="Pending",
                        node_name="worker-a",
                        pod_ip="10.2.0.11",
                    ),
                ]
            )
        )

        result = KubernetesPodService(api=api).list_namespace_pods(
            NamespaceScope(namespace="payments")
        )

        self.assertEqual(result.namespace, "payments")
        self.assertEqual(result.count, 2)
        self.assertEqual([pod.name for pod in result.pods], ["api-a", "api-b"])
        self.assertEqual(result.pods[0].phase, "Pending")


if __name__ == "__main__":
    unittest.main()
