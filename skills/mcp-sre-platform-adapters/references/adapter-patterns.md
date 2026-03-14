# Adapter Patterns

## Kubernetes

- Load kubeconfig from `MCP_KUBECONFIG` when set.
- Select kube context from `MCP_KUBE_CONTEXT` when set.
- Fall back to in-cluster config if kubeconfig is unavailable.
- Mask kubeconfig paths in logs.
- Strip raw API exception details before returning errors to tools.

## Prometheus

- Separate instant queries from range queries.
- Bound range queries by `start`, `end`, and `step`.
- Reduce result series before returning them to the MCP layer.

## Security

- Never expose raw secrets, tokens, or full local paths in logs.
- Never return raw secret-bearing manifests to the MCP client.
- Prefer summaries and typed records over pass-through payloads.
