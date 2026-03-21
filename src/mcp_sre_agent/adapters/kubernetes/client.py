"""Kubernetes client construction."""

from __future__ import annotations

from functools import lru_cache

from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException

from mcp_sre_agent.adapters.kubernetes.config import KubernetesConfigurationError
from mcp_sre_agent.app.config import get_settings


@lru_cache(maxsize=1)
def build_core_v1_api() -> client.CoreV1Api:
    """Create a configured CoreV1Api client."""

    settings = get_settings()

    try:
        config.load_kube_config(
            config_file=settings.kubeconfig,
            context=settings.kube_context,
        )
    except ConfigException:
        try:
            config.load_incluster_config()
        except ConfigException as exc:
            raise KubernetesConfigurationError(
                "Unable to load Kubernetes configuration from kubeconfig or in-cluster settings."
            ) from exc

    return client.CoreV1Api()


@lru_cache(maxsize=1)
def build_apps_v1_api() -> client.AppsV1Api:
    """Create a configured AppsV1Api client."""

    # Ensure shared configuration has been loaded exactly once.
    build_core_v1_api()
    return client.AppsV1Api()
