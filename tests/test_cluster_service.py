"""Unit tests for the cluster Kubernetes service."""

from __future__ import annotations

import unittest
from types import SimpleNamespace

from mcp_sre_agent.adapters.kubernetes import KubernetesClusterService


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


if __name__ == "__main__":
    unittest.main()
