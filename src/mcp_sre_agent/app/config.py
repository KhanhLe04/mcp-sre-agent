"""Configuration helpers for the MCP SRE agent package."""

from __future__ import annotations

from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings shared across MCP servers and adapters."""

    app_name: str = "mcp-sre-agent"
    log_level: str = "INFO"
    default_server: str = "cluster"
    default_transport: str = "stdio"
    host: str = "127.0.0.1"
    port: int = 8000
    sse_path: str = "/sse"
    message_path: str = "/messages/"
    streamable_http_path: str = "/mcp"
    kubeconfig: str | None = Field(
        default=None,
        validation_alias=AliasChoices("MCP_KUBECONFIG", "KUBECONFIG"),
    )
    kube_context: str | None = Field(
        default=None,
        validation_alias=AliasChoices("MCP_KUBE_CONTEXT", "KUBE_CONTEXT"),
    )

    model_config = SettingsConfigDict(
        env_prefix="MCP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached package settings."""

    return Settings()
