"""Shared low-level helpers for MCP server tool handlers."""

from __future__ import annotations

from pydantic import ValidationError

from mcp_sre_agent.adapters.kubernetes import KubernetesAccessError
from mcp_sre_agent.domain.common import ErrorCategory, NamespaceScope
from mcp_sre_agent.servers.errors import raise_tool_error


def validate_required_string(value: str, *, field_name: str) -> str:
    """Validate that a string input is present and non-empty."""

    if not isinstance(value, str) or not value.strip():
        raise_tool_error(
            category=ErrorCategory.INVALID_INPUT,
            message=f"{field_name} must be a non-empty string.",
        )
    return value.strip()


def validate_limit(value: int, *, field_name: str, minimum: int = 1, maximum: int = 100) -> int:
    """Validate a bounded integer limit."""

    if not isinstance(value, int) or value < minimum or value > maximum:
        raise_tool_error(
            category=ErrorCategory.INVALID_INPUT,
            message=f"{field_name} must be an integer between {minimum} and {maximum}.",
        )
    return value


def validate_namespace(namespace: str) -> NamespaceScope:
    """Validate namespace scope and return normalized scope."""

    try:
        return NamespaceScope(namespace=namespace.strip())
    except (ValidationError, AttributeError):
        raise_tool_error(
            category=ErrorCategory.INVALID_INPUT,
            message="namespace must be a non-empty string.",
        )


def raise_kubernetes_error(exc: KubernetesAccessError) -> None:
    """Map Kubernetes access errors into safe MCP tool errors."""

    message = str(exc)
    category = ErrorCategory.NOT_FOUND if "was not found" in message else ErrorCategory.UPSTREAM_UNAVAILABLE
    raise_tool_error(
        category=category,
        message=message,
        retryable=category == ErrorCategory.UPSTREAM_UNAVAILABLE,
    )
