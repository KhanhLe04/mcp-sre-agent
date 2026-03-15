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

### Current usage

Configuration precedence:

1. Explicit process environment variables
2. Local `.env` file
3. Defaults in `src/mcp_sre_agent/app/config.py`

Run the cluster MCP server over stdio:

```bash
uv run mcp-sre-agent cluster
```

Run the cluster MCP server over Streamable HTTP:

```bash
uv run mcp-sre-agent cluster --transport streamable-http
```

Override the kube context when needed:

```bash
MCP_KUBE_CONTEXT=my-context uv run mcp-sre-agent cluster
```

Point to a specific kubeconfig file when needed:

```bash
MCP_KUBECONFIG=/path/to/config uv run mcp-sre-agent cluster
```

Override HTTP bind settings for local, Docker, or Kubernetes deployments:

```bash
MCP_HOST=0.0.0.0 MCP_PORT=8080 MCP_STREAMABLE_HTTP_PATH=/mcp uv run mcp-sre-agent cluster --transport streamable-http
```

Available server env settings:

- `MCP_HOST`
- `MCP_PORT`
- `MCP_STREAMABLE_HTTP_PATH`
- `MCP_SSE_PATH`
- `MCP_MESSAGE_PATH`
- `MCP_DEFAULT_TRANSPORT`
- `MCP_DEFAULT_SERVER`
- `MCP_LOG_LEVEL`
- `MCP_KUBECONFIG`
- `MCP_KUBE_CONTEXT`
