"""Kubernetes workload and service health operations."""

from __future__ import annotations

from typing import Literal

from kubernetes import client
from kubernetes.client.exceptions import ApiException

from mcp_sre_agent.adapters.kubernetes.client import build_apps_v1_api, build_core_v1_api
from mcp_sre_agent.adapters.kubernetes.nodes import KubernetesAccessError
from mcp_sre_agent.app.config import get_settings
from mcp_sre_agent.domain.cluster import (
    ControllerTargetType,
    FindWorkloadsResult,
    PodHealthSummary,
    WorkloadMatch,
    WorkloadCondition,
    WorkloadHealthResult,
    WorkloadPodsResult,
    WorkloadStatusResult,
    WorkloadTargetType,
)


def _conditions(raw_conditions: list[object] | None) -> list[WorkloadCondition]:
    if not raw_conditions:
        return []

    return [
        WorkloadCondition(
            type=getattr(item, "type", "Unknown"),
            status=getattr(item, "status", "Unknown"),
            reason=getattr(item, "reason", None),
            message=getattr(item, "message", None),
        )
        for item in raw_conditions
    ]


def _restart_count(container_statuses: list[object] | None) -> int:
    if not container_statuses:
        return 0
    return sum(int(getattr(status, "restart_count", 0) or 0) for status in container_statuses)


def _pod_ready(pod: object) -> bool:
    conditions = getattr(getattr(pod, "status", None), "conditions", None)
    if not conditions:
        return False
    for condition in conditions:
        if getattr(condition, "type", None) == "Ready":
            return getattr(condition, "status", None) == "True"
    return False


def _pod_reason(pod: object) -> str | None:
    statuses = getattr(getattr(pod, "status", None), "container_statuses", None) or []
    for status in statuses:
        waiting = getattr(getattr(status, "state", None), "waiting", None)
        if waiting and getattr(waiting, "reason", None):
            return waiting.reason
        terminated = getattr(getattr(status, "state", None), "terminated", None)
        if terminated and getattr(terminated, "reason", None):
            return terminated.reason
    return getattr(getattr(pod, "status", None), "reason", None)


def _pod_summary(pod: object) -> PodHealthSummary:
    return PodHealthSummary(
        name=pod.metadata.name,
        namespace=pod.metadata.namespace,
        phase=getattr(pod.status, "phase", None),
        ready=_pod_ready(pod),
        restart_count=_restart_count(getattr(pod.status, "container_statuses", None)),
        reason=_pod_reason(pod),
        node_name=getattr(pod.spec, "node_name", None),
        pod_ip=getattr(pod.status, "pod_ip", None),
    )


def _selector_to_query(selector: dict[str, str]) -> str:
    return ",".join(f"{key}={value}" for key, value in sorted(selector.items()))


class KubernetesWorkloadService:
    """Service layer for workload and service health reads."""

    def __init__(
        self,
        *,
        core_api: client.CoreV1Api | None = None,
        apps_api: client.AppsV1Api | None = None,
    ) -> None:
        self._core_api = core_api or build_core_v1_api()
        self._apps_api = apps_api or build_apps_v1_api()
        self._settings = get_settings()

    def get_deployment_status(self, namespace: str, name: str) -> WorkloadStatusResult:
        return self._controller_status("deployment", namespace, name)

    def get_statefulset_status(self, namespace: str, name: str) -> WorkloadStatusResult:
        return self._controller_status("statefulset", namespace, name)

    def get_daemonset_status(self, namespace: str, name: str) -> WorkloadStatusResult:
        return self._controller_status("daemonset", namespace, name)

    def get_pod_status(self, namespace: str, name: str) -> PodHealthSummary:
        try:
            pod = self._core_api.read_namespaced_pod(namespace=namespace, name=name)
        except ApiException as exc:
            if exc.status == 404:
                raise KubernetesAccessError(
                    f"Kubernetes pod '{namespace}/{name}' was not found."
                ) from exc
            raise KubernetesAccessError(
                f"Kubernetes API request failed while fetching pod '{namespace}/{name}'."
            ) from exc
        return _pod_summary(pod)

    def find_workloads(
        self,
        query: str,
        *,
        namespace: str | None = None,
        limit: int = 20,
    ) -> FindWorkloadsResult:
        """Find likely workload or service targets by partial name match."""

        normalized_query = query.strip().lower()
        matches: list[WorkloadMatch] = []

        for target_type, items in (
            ("service", self._list_services(namespace)),
            ("deployment", self._list_deployments(namespace)),
            ("statefulset", self._list_statefulsets(namespace)),
            ("daemonset", self._list_daemonsets(namespace)),
        ):
            for item in items:
                name = item.metadata.name
                item_namespace = item.metadata.namespace
                if normalized_query in name.lower():
                    matches.append(
                        WorkloadMatch(
                            namespace=item_namespace,
                            target_type=target_type,
                            target_name=name,
                        )
                    )

        matches.sort(key=lambda item: (item.namespace, item.target_type, item.target_name))
        matches = matches[:limit]

        return FindWorkloadsResult(
            cluster=self._settings.kube_context,
            query=query,
            namespace=namespace,
            count=len(matches),
            matches=matches,
        )

    def list_workload_pods(
        self,
        target_type: WorkloadTargetType,
        namespace: str,
        target_name: str,
    ) -> WorkloadPodsResult:
        selector = self._selector_for_target(target_type, namespace, target_name)
        pods = self._pods_for_selector(namespace, selector)
        return WorkloadPodsResult(
            cluster=self._settings.kube_context,
            namespace=namespace,
            target_type=target_type,
            target_name=target_name,
            count=len(pods),
            selector=selector,
            pods=pods,
        )

    def get_workload_health(
        self,
        target_type: WorkloadTargetType,
        namespace: str,
        target_name: str,
    ) -> WorkloadHealthResult:
        pods_result = self.list_workload_pods(target_type, namespace, target_name)
        status = None
        desired = None
        ready = None

        if target_type != "service":
            status = self._controller_status(
                target_type,  # type: ignore[arg-type]
                namespace,
                target_name,
            )
            desired = status.desired_replicas
            ready = status.ready_replicas
        else:
            desired = pods_result.count
            ready = sum(1 for pod in pods_result.pods if pod.ready)

        unhealthy = [pod for pod in pods_result.pods if not pod.ready or pod.phase != "Running"]
        unhealthy_count = len(unhealthy)
        issues: list[str] = []

        if pods_result.count == 0:
            overall = "unknown"
            issues.append("No pods matched the target selector.")
        elif unhealthy_count == 0 and (desired is None or (ready is not None and ready >= desired)):
            overall = "healthy"
        elif (ready or 0) > 0:
            overall = "degraded"
        else:
            overall = "unhealthy"

        if desired is not None and ready is not None and ready < desired:
            issues.append(f"Ready replicas ({ready}) are below desired replicas ({desired}).")
        if unhealthy_count > 0:
            issues.append(f"{unhealthy_count} pod(s) are not healthy.")

        summary = (
            f"{target_type} '{namespace}/{target_name}' is {overall}: "
            f"{ready or 0}/{desired if desired is not None else pods_result.count} healthy pods."
        )

        return WorkloadHealthResult(
            cluster=self._settings.kube_context,
            namespace=namespace,
            target_type=target_type,
            target_name=target_name,
            overall_status=overall,
            summary=summary,
            total_pods=pods_result.count,
            unhealthy_pods=unhealthy_count,
            desired_replicas=desired,
            ready_replicas=ready,
            issues=issues,
            pods=pods_result.pods,
            status=status,
        )

    def _controller_status(
        self,
        controller_type: ControllerTargetType,
        namespace: str,
        name: str,
    ) -> WorkloadStatusResult:
        try:
            if controller_type == "deployment":
                obj = self._apps_api.read_namespaced_deployment(namespace=namespace, name=name)
                desired = getattr(obj.spec, "replicas", None)
                ready = getattr(obj.status, "ready_replicas", None)
                updated = getattr(obj.status, "updated_replicas", None)
                available = getattr(obj.status, "available_replicas", None)
            elif controller_type == "statefulset":
                obj = self._apps_api.read_namespaced_stateful_set(namespace=namespace, name=name)
                desired = getattr(obj.spec, "replicas", None)
                ready = getattr(obj.status, "ready_replicas", None)
                updated = getattr(obj.status, "updated_replicas", None)
                available = getattr(obj.status, "available_replicas", None)
            else:
                obj = self._apps_api.read_namespaced_daemon_set(namespace=namespace, name=name)
                desired = getattr(obj.status, "desired_number_scheduled", None)
                ready = getattr(obj.status, "number_ready", None)
                updated = getattr(obj.status, "updated_number_scheduled", None)
                available = getattr(obj.status, "number_available", None)
        except ApiException as exc:
            if exc.status == 404:
                raise KubernetesAccessError(
                    f"Kubernetes {controller_type} '{namespace}/{name}' was not found."
                ) from exc
            raise KubernetesAccessError(
                f"Kubernetes API request failed while fetching {controller_type} '{namespace}/{name}'."
            ) from exc

        selector = getattr(getattr(obj.spec, "selector", None), "match_labels", None) or {}
        return WorkloadStatusResult(
            cluster=self._settings.kube_context,
            namespace=namespace,
            target_type=controller_type,
            target_name=name,
            desired_replicas=desired,
            ready_replicas=ready,
            updated_replicas=updated,
            available_replicas=available,
            observed_generation=getattr(obj.status, "observed_generation", None),
            selector=selector,
            conditions=_conditions(getattr(obj.status, "conditions", None)),
        )

    def _selector_for_target(
        self,
        target_type: WorkloadTargetType,
        namespace: str,
        target_name: str,
    ) -> dict[str, str]:
        if target_type == "service":
            try:
                service = self._core_api.read_namespaced_service(namespace=namespace, name=target_name)
            except ApiException as exc:
                if exc.status == 404:
                    raise KubernetesAccessError(
                        f"Kubernetes service '{namespace}/{target_name}' was not found."
                    ) from exc
                raise KubernetesAccessError(
                    f"Kubernetes API request failed while fetching service '{namespace}/{target_name}'."
                ) from exc
            selector = getattr(service.spec, "selector", None) or {}
        elif target_type == "deployment":
            selector = self.get_deployment_status(namespace, target_name).selector
        elif target_type == "statefulset":
            selector = self.get_statefulset_status(namespace, target_name).selector
        else:
            selector = self.get_daemonset_status(namespace, target_name).selector

        if not selector:
            raise KubernetesAccessError(
                f"No selector labels found for {target_type} '{namespace}/{target_name}'."
            )
        return selector

    def _pods_for_selector(self, namespace: str, selector: dict[str, str]) -> list[PodHealthSummary]:
        label_selector = _selector_to_query(selector)
        try:
            items = self._core_api.list_namespaced_pod(
                namespace=namespace,
                label_selector=label_selector,
            ).items
        except ApiException as exc:
            raise KubernetesAccessError(
                f"Kubernetes API request failed while listing pods in namespace '{namespace}'."
            ) from exc
        pods = [_pod_summary(item) for item in items]
        pods.sort(key=lambda item: item.name)
        return pods

    def _list_services(self, namespace: str | None) -> list[object]:
        try:
            if namespace:
                return self._core_api.list_namespaced_service(namespace=namespace).items
            return self._core_api.list_service_for_all_namespaces().items
        except ApiException as exc:
            raise KubernetesAccessError("Kubernetes API request failed while listing services.") from exc

    def _list_deployments(self, namespace: str | None) -> list[object]:
        try:
            if namespace:
                return self._apps_api.list_namespaced_deployment(namespace=namespace).items
            return self._apps_api.list_deployment_for_all_namespaces().items
        except ApiException as exc:
            raise KubernetesAccessError("Kubernetes API request failed while listing deployments.") from exc

    def _list_statefulsets(self, namespace: str | None) -> list[object]:
        try:
            if namespace:
                return self._apps_api.list_namespaced_stateful_set(namespace=namespace).items
            return self._apps_api.list_stateful_set_for_all_namespaces().items
        except ApiException as exc:
            raise KubernetesAccessError("Kubernetes API request failed while listing statefulsets.") from exc

    def _list_daemonsets(self, namespace: str | None) -> list[object]:
        try:
            if namespace:
                return self._apps_api.list_namespaced_daemon_set(namespace=namespace).items
            return self._apps_api.list_daemon_set_for_all_namespaces().items
        except ApiException as exc:
            raise KubernetesAccessError("Kubernetes API request failed while listing daemonsets.") from exc
