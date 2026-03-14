"""Configuration helpers for the MCP SRE agent package."""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    """Minimal runtime settings used by the bootstrap layer."""

    app_name: str = "mcp-sre-agent"
    log_level: str = os.getenv("MCP_SRE_AGENT_LOG_LEVEL", "INFO")


def get_settings() -> Settings:
    """Return package settings without introducing external dependencies yet."""

    return Settings()
