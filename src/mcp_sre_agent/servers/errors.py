"""Helpers for converting internal exceptions into safe MCP-facing errors."""

from __future__ import annotations

from mcp_sre_agent.domain.common import ErrorCategory, ToolError


def raise_tool_error(
    *,
    category: ErrorCategory,
    message: str,
    retryable: bool = False,
) -> None:
    """Raise a runtime error with a serialized safe tool error payload."""

    error = ToolError(category=category, message=message, retryable=retryable)
    raise RuntimeError(error.model_dump_json())
