"""Tests for shared domain primitives."""

from __future__ import annotations

from datetime import datetime
import unittest

from mcp_sre_agent.domain.common import (
    ClusterScope,
    ErrorCategory,
    NamespaceScope,
    TimeWindow,
    ToolError,
    WorkloadScope,
)


class DomainCommonTests(unittest.TestCase):
    def test_time_window_rejects_reversed_range(self) -> None:
        with self.assertRaises(ValueError):
            TimeWindow(
                start=datetime(2026, 3, 15, 10, 0, 0),
                end=datetime(2026, 3, 15, 9, 0, 0),
            )

    def test_scope_models_capture_expected_fields(self) -> None:
        cluster = ClusterScope(cluster="prod")
        namespace = NamespaceScope(cluster="prod", namespace="payments")
        workload = WorkloadScope(
            cluster="prod",
            namespace="payments",
            kind="deployment",
            name="checkout",
        )

        self.assertEqual(cluster.cluster, "prod")
        self.assertEqual(namespace.namespace, "payments")
        self.assertEqual(workload.kind, "deployment")
        self.assertEqual(workload.name, "checkout")

    def test_tool_error_uses_shared_error_category(self) -> None:
        error = ToolError(
            category=ErrorCategory.UPSTREAM_UNAVAILABLE,
            message="Prometheus is unavailable.",
            retryable=True,
        )

        self.assertEqual(error.category, ErrorCategory.UPSTREAM_UNAVAILABLE)
        self.assertTrue(error.retryable)


if __name__ == "__main__":
    unittest.main()
