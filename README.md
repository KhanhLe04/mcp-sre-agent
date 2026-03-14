## mcp-sre-agent

SRE-focused MCP servers for Kubernetes, metrics, logs, and investigation workflows.

### Current foundation

- `uv`-managed Python package
- `src/` layout
- Base package modules for app, adapters, domain, servers, storage, and workflows
- Local `skills/` folder reserved for project-specific Codex skills

### Planned implementation order

1. Shared config and domain schemas
2. Kubernetes cluster server
3. Prometheus metrics server
4. Investigation workflow
5. Logs and deploy correlation
