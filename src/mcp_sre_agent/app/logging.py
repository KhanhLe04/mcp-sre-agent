"""Logging helpers with conservative output for local and server runtime."""

from __future__ import annotations

import logging

from mcp_sre_agent.adapters.kubernetes import KubernetesConnectionInfo
from mcp_sre_agent.app.config import Settings


def configure_logging(settings: Settings) -> None:
    """Configure package logging once at process startup."""

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def log_server_start(
    *,
    settings: Settings,
    server_name: str,
    transport: str,
    kube: KubernetesConnectionInfo | None = None,
) -> None:
    """Log sanitized startup information."""

    logger = logging.getLogger("mcp_sre_agent.startup")
    logger.info("starting server=%s transport=%s", server_name, transport)

    if transport == "streamable-http":
        logger.info(
            "streamable-http bind=http://%s:%s%s",
            settings.host,
            settings.port,
            settings.streamable_http_path,
        )
    elif transport == "sse":
        logger.info(
            "sse bind=http://%s:%s%s messages=%s",
            settings.host,
            settings.port,
            settings.sse_path,
            settings.message_path,
        )

    if kube is not None:
        logger.info(
            "kubernetes source=%s kubeconfig=%s context=%s",
            kube.source,
            kube.kubeconfig_label,
            kube.context or "<default>",
        )
