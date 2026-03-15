"""Shared domain primitives used across servers and workflows."""

from mcp_sre_agent.domain.common.errors import ErrorCategory, ToolError
from mcp_sre_agent.domain.common.metadata import ResponseMetadata
from mcp_sre_agent.domain.common.scope import ClusterScope, NamespaceScope, WorkloadScope
from mcp_sre_agent.domain.common.time_windows import TimeWindow

__all__ = [
    "ClusterScope",
    "ErrorCategory",
    "NamespaceScope",
    "ResponseMetadata",
    "TimeWindow",
    "ToolError",
    "WorkloadScope",
]
