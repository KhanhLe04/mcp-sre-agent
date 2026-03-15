"""Shared time window models."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, model_validator


class TimeWindow(BaseModel):
    """A bounded time range used by metrics, logs, and investigations."""

    start: datetime
    end: datetime

    @model_validator(mode="after")
    def validate_order(self) -> "TimeWindow":
        """Ensure the end is not earlier than the start."""

        if self.end < self.start:
            raise ValueError("end must be greater than or equal to start")

        return self
