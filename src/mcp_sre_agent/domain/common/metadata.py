"""Shared response metadata models."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ResponseMetadata(BaseModel):
    """Lightweight metadata that can be attached to typed tool outputs later."""

    source_system: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
