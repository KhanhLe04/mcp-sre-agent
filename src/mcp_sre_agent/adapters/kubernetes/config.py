"""Kubernetes configuration helpers."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

from mcp_sre_agent.app.config import get_settings


class KubernetesConfigurationError(RuntimeError):
    """Raised when no Kubernetes configuration can be loaded."""


@dataclass(frozen=True)
class KubernetesConnectionInfo:
    """Sanitized information about how the adapter is configured to connect."""

    source: str
    kubeconfig_label: str
    context: str | None
    mcp_kubeconfig_defined: bool
    mcp_kube_context_defined: bool
    kubeconfig_fallback_defined: bool
    kube_context_fallback_defined: bool


def _mask_path(path: str | None) -> str:
    if not path:
        return "<default>"

    name = Path(path).name
    return f".../{name}" if name else "<default>"


def planned_connection_info() -> KubernetesConnectionInfo:
    """Return sanitized connection intent before loading any credentials."""

    settings = get_settings()
    return KubernetesConnectionInfo(
        source="kubeconfig-or-incluster",
        kubeconfig_label=_mask_path(settings.kubeconfig),
        context=settings.kube_context,
        mcp_kubeconfig_defined=bool(os.environ.get("MCP_KUBECONFIG")),
        mcp_kube_context_defined=bool(os.environ.get("MCP_KUBE_CONTEXT")),
        kubeconfig_fallback_defined=bool(os.environ.get("KUBECONFIG")),
        kube_context_fallback_defined=bool(os.environ.get("KUBE_CONTEXT")),
    )
