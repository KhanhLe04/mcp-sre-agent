"""Shared error primitives."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel


class ErrorCategory(StrEnum):
    """Common safe error categories for MCP tool responses."""

    INVALID_INPUT = "invalid_input"
    NOT_FOUND = "not_found"
    UNAUTHORIZED = "unauthorized"
    UPSTREAM_UNAVAILABLE = "upstream_unavailable"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    INTERNAL = "internal"


class ToolError(BaseModel):
    """A safe, structured representation of a tool-level error."""

    category: ErrorCategory
    message: str
    retryable: bool = False
