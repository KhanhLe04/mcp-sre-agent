"""Tests for sanitized Kubernetes configuration and errors."""

from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from kubernetes.client.exceptions import ApiException

from mcp_sre_agent.adapters.kubernetes import (
    KubernetesAccessError,
    KubernetesClusterService,
    planned_connection_info,
)
from mcp_sre_agent.app.config import get_settings
from mcp_sre_agent.domain.common import ErrorCategory
from mcp_sre_agent.servers.errors import raise_tool_error


class KubernetesSecurityTests(unittest.TestCase):
    def tearDown(self) -> None:
        get_settings.cache_clear()

    def test_planned_connection_info_masks_kubeconfig_path(self) -> None:
        with patch.dict(
            "os.environ",
            {
                "MCP_KUBECONFIG": r"C:\Users\Khanh\.kube\prod-config",
                "MCP_KUBE_CONTEXT": "prod",
            },
            clear=False,
        ):
            get_settings.cache_clear()
            info = planned_connection_info()

        self.assertEqual(info.kubeconfig_label, ".../prod-config")
        self.assertEqual(info.context, "prod")

    def test_list_nodes_raises_sanitized_error(self) -> None:
        class FailingApi:
            def list_node(self) -> None:
                raise ApiException(reason="token leaked here")

        service = KubernetesClusterService(api=FailingApi())

        with self.assertRaises(KubernetesAccessError) as context:
            service.list_nodes()

        self.assertEqual(
            str(context.exception),
            "Kubernetes API request failed while listing nodes.",
        )

    def test_raise_tool_error_serializes_safe_payload(self) -> None:
        with self.assertRaises(RuntimeError) as context:
            raise_tool_error(
                category=ErrorCategory.UPSTREAM_UNAVAILABLE,
                message="Prometheus is unavailable.",
                retryable=True,
            )

        payload = json.loads(str(context.exception))
        self.assertEqual(payload["category"], "upstream_unavailable")
        self.assertEqual(payload["message"], "Prometheus is unavailable.")
        self.assertTrue(payload["retryable"])


if __name__ == "__main__":
    unittest.main()
