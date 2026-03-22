"""Tests for Kubernetes pod and deployment creation."""

from __future__ import annotations

import unittest

from mcp_sre_agent.adapters.kubernetes.creation import KubernetesCreationService
from mcp_sre_agent.domain.cluster import ContainerSpec, CreateDeploymentRequest, CreatePodRequest, DeploymentSpec


class _FakeCoreApi:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    def create_namespaced_pod(self, namespace: str, body: object) -> None:
        self.calls.append((namespace, body))


class _FakeAppsApi:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    def create_namespaced_deployment(self, namespace: str, body: object) -> None:
        self.calls.append((namespace, body))


class ContainerSpecTests(unittest.TestCase):
    def test_normalizes_port_from_legacy_ports_int(self) -> None:
        spec = ContainerSpec(name="nginx", image="nginx:latest", ports=[80])

        self.assertEqual(spec.port, 80)

    def test_normalizes_port_from_legacy_ports_object(self) -> None:
        spec = ContainerSpec(name="nginx", image="nginx:latest", ports=[{"containerPort": 80}])

        self.assertEqual(spec.port, 80)


class KubernetesCreationServiceTests(unittest.TestCase):
    def test_create_pod_uses_typed_container_spec(self) -> None:
        core_api = _FakeCoreApi()
        service = KubernetesCreationService(core_api=core_api, apps_api=_FakeAppsApi())
        request = CreatePodRequest(
            name="nginx",
            namespace="default",
            containers=[ContainerSpec(name="nginx", image="nginx:latest", ports=[80])],
        )

        result = service.create_pod(request)

        self.assertTrue(result.success)
        self.assertEqual(len(core_api.calls), 1)
        namespace, body = core_api.calls[0]
        self.assertEqual(namespace, "default")
        self.assertEqual(body.metadata.name, "nginx")
        self.assertEqual(body.spec.containers[0].ports[0].container_port, 80)

    def test_create_deployment_keeps_selector_labels_in_sync(self) -> None:
        apps_api = _FakeAppsApi()
        service = KubernetesCreationService(core_api=_FakeCoreApi(), apps_api=apps_api)
        request = CreateDeploymentRequest(
            name="nginx",
            namespace="default",
            containers=[ContainerSpec(name="nginx", image="nginx:latest", ports=[{"containerPort": 80}])],
            deployment_spec=DeploymentSpec(replicas=3),
        )

        result = service.create_deployment(request)

        self.assertTrue(result.success)
        self.assertEqual(len(apps_api.calls), 1)
        namespace, body = apps_api.calls[0]
        self.assertEqual(namespace, "default")
        self.assertEqual(body.spec.selector.match_labels, {"app": "nginx"})
        self.assertEqual(body.spec.template.metadata.labels, {"app": "nginx"})
        self.assertEqual(body.spec.template.spec.containers[0].ports[0].container_port, 80)


if __name__ == "__main__":
    unittest.main()
