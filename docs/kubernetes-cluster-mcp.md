# Kubernetes Cluster MCP Tool

## Summary

This document explains the Kubernetes MCP capability currently implemented in this repository. It is intended for contributors who need to understand how the server is structured, how it connects to Kubernetes, how it is configured and secured, and how to extend it safely.

At the moment, the project exposes one MCP server, `cluster`, with one tool, `list_nodes`. The implementation is intentionally narrow: it proves the project structure, transport model, Kubernetes integration path, and baseline security posture before more tools are added.

## Current Scope

The current Kubernetes MCP implementation provides:

- one FastMCP server named `cluster`
- one tool named `list_nodes`
- Kubernetes client initialization through kubeconfig or in-cluster configuration
- typed, reduced responses instead of raw Kubernetes API objects
- configurable MCP transports and HTTP bind settings
- sanitized startup logging and sanitized upstream error handling

It does not yet provide:

- write operations against the Kubernetes API
- namespace-scoped workload or pod inspection
- RBAC introspection
- caching beyond Python process-level object reuse
- health endpoints or readiness probes
- persistent investigation state

## Why This Tool Exists

The `cluster` server is the first concrete slice of the larger SRE-focused MCP platform.

Its goals are:

- validate the MCP server layout
- validate Kubernetes connectivity and configuration rules
- establish the adapter-domain-server separation used by future tools
- establish safe operational defaults before broader cluster visibility is added

This tool should be treated as the reference pattern for future Kubernetes-facing tools.

## High-Level Architecture

The implementation is split into four layers.

### 1. CLI and startup layer

File: `src/mcp_sre_agent/cli.py`

Responsibilities:

- parse the selected server and transport
- load settings from environment variables
- configure logging
- emit sanitized startup logs
- create and run the selected MCP server

### 2. MCP server layer

Files:

- `src/mcp_sre_agent/servers/cluster/server.py`
- `src/mcp_sre_agent/servers/cluster/tools_nodes.py`

Responsibilities:

- create a `FastMCP` server named `cluster`
- configure server host, port, log level, and HTTP paths from settings
- register the `list_nodes` MCP tool
- translate sanitized adapter errors into safe MCP-facing runtime errors

### 3. Adapter and service layer

Files:

- `src/mcp_sre_agent/adapters/kubernetes/config.py`
- `src/mcp_sre_agent/adapters/kubernetes/client.py`
- `src/mcp_sre_agent/adapters/kubernetes/nodes.py`

Responsibilities:

- load Kubernetes configuration
- build the Kubernetes `CoreV1Api` client
- encapsulate the cluster read logic in `KubernetesClusterService`
- reduce Kubernetes node objects into a small typed summary
- sanitize configuration and API errors

### 4. Domain model layer

Files:

- `src/mcp_sre_agent/domain/cluster/__init__.py`
- `src/mcp_sre_agent/domain/cluster/nodes.py`

Responsibilities:

- define the typed output models returned by the tool
- keep the MCP surface stable even if upstream Kubernetes objects change

## Request Flow

The request flow for `list_nodes` is:

1. A host or client starts the `cluster` server through the CLI.
2. The CLI loads `Settings` and configures logging.
3. The CLI logs the selected transport and sanitized Kubernetes connection intent.
4. The CLI creates the `cluster` FastMCP server and starts the requested transport.
5. The MCP client invokes the `list_nodes` tool.
6. The server calls `get_cluster_service().list_nodes()`.
7. The service initializes `CoreV1Api` on first use through `build_core_v1_api()`.
8. The adapter loads Kubernetes configuration from kubeconfig or in-cluster config.
9. The adapter calls `CoreV1Api.list_node()`.
10. The adapter reduces each node to a `NodeSummary`.
11. The tool returns a `ListNodesResult` to the MCP client.

## Code Map

The current implementation is centered in these files:

- `src/mcp_sre_agent/cli.py`
- `src/mcp_sre_agent/app/config.py`
- `src/mcp_sre_agent/app/logging.py`
- `src/mcp_sre_agent/servers/cluster/server.py`
- `src/mcp_sre_agent/servers/cluster/tools_nodes.py`
- `src/mcp_sre_agent/adapters/kubernetes/config.py`
- `src/mcp_sre_agent/adapters/kubernetes/client.py`
- `src/mcp_sre_agent/adapters/kubernetes/nodes.py`
- `src/mcp_sre_agent/domain/cluster/nodes.py`
- `tests/test_cluster_service.py`
- `tests/test_kubernetes_security.py`

## Tool Contract

### Tool name

`list_nodes`

### Purpose

Return a reduced summary of available Kubernetes nodes.

### Output model

The tool returns `ListNodesResult`, which contains:

- `cluster`: selected kube context when provided, otherwise `null`
- `count`: total number of returned nodes
- `nodes`: list of `NodeSummary`

Each `NodeSummary` currently contains:

- `name`
- `ready`
- `roles`
- `internal_ip`
- `kubelet_version`
- `os_image`
- `container_runtime`

### Why the output is reduced

The server does not return raw Kubernetes node objects because that would create unnecessary coupling to upstream schemas, increase token cost, and increase the chance of leaking irrelevant fields. The project standard is to return reduced, typed, task-specific data structures.

## Transport Model

The server supports three MCP transports:

- `stdio`
- `sse`
- `streamable-http`

### `stdio`

This is the default transport. It is appropriate when an MCP host launches the server directly and communicates over stdin/stdout. If started manually in a terminal, it will appear idle because it is waiting for an MCP client.

### `sse`

This is available for HTTP-based server operation using Server-Sent Events.

### `streamable-http`

This is the preferred transport for manual local testing, Docker deployment, and Kubernetes deployment. With the current settings defaults, the endpoint is:

- `http://127.0.0.1:8000/mcp`

unless overridden through `MCP_HOST`, `MCP_PORT`, and `MCP_STREAMABLE_HTTP_PATH`.

## Configuration

The runtime configuration is defined in `src/mcp_sre_agent/app/config.py` using `pydantic-settings`.

### Supported environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `MCP_DEFAULT_SERVER` | `cluster` | Default server selected by the CLI |
| `MCP_DEFAULT_TRANSPORT` | `stdio` | Default transport when `--transport` is omitted |
| `MCP_LOG_LEVEL` | `INFO` | Logging verbosity |
| `MCP_HOST` | `127.0.0.1` | HTTP bind host for SSE and Streamable HTTP |
| `MCP_PORT` | `8000` | HTTP bind port |
| `MCP_SSE_PATH` | `/sse` | SSE endpoint path |
| `MCP_MESSAGE_PATH` | `/messages/` | SSE message path |
| `MCP_STREAMABLE_HTTP_PATH` | `/mcp` | Streamable HTTP MCP endpoint path |
| `MCP_KUBECONFIG` | unset | Explicit path to kubeconfig |
| `MCP_KUBE_CONTEXT` | unset | Explicit context inside the kubeconfig |

## Kubernetes Configuration Resolution

The adapter resolves Kubernetes access in this order:

1. call `load_kube_config(config_file=settings.kubeconfig, context=settings.kube_context)`
2. if kubeconfig loading fails, call `load_incluster_config()`
3. if both fail, raise `KubernetesConfigurationError`

### Meaning of `MCP_KUBECONFIG`

This selects the kubeconfig file path to load.

### Meaning of `MCP_KUBE_CONTEXT`

This selects the context inside that kubeconfig file.

### Important distinction

`MCP_KUBECONFIG` points to the file.
`MCP_KUBE_CONTEXT` chooses the profile inside the file.

If `MCP_KUBE_CONTEXT` is not set, the Kubernetes client uses the kubeconfig default or current context.

## Logging and Security Posture

The current implementation makes a deliberate tradeoff: contributors should be able to see enough startup information to debug configuration, but not enough to leak secrets or sensitive local details.

### Startup logging

The startup logger prints:

- selected server
- selected transport
- HTTP bind address for HTTP-based transports
- sanitized Kubernetes connection intent

Example:

```text
starting server=cluster transport=streamable-http
streamable-http bind=http://0.0.0.0:8080/mcp
kubernetes source=kubeconfig-or-incluster kubeconfig=.../prod-config context=prod
```

### Redaction behavior

The kubeconfig path is masked to `.../<filename>` instead of logging the full local path.

### Sanitized errors

When Kubernetes API access fails during `list_nodes`, the adapter raises:

- `KubernetesAccessError("Kubernetes API request failed while listing nodes.")`

This prevents raw upstream exception details from leaking through MCP responses or logs.

### Prompt injection and secret-handling implications

This server currently reduces the secret-exposure surface in these ways:

- it does not expose a tool that reads environment variables
- it does not expose kubeconfig file contents
- it does not return raw Kubernetes objects
- it does not log full kubeconfig paths
- it does not forward raw Kubernetes API exception bodies to the caller

Contributors must preserve this posture when adding tools.

## Local Development

### Create or update the environment

```powershell
uv sync
```

### Run tests

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

### Run with stdio

```powershell
uv run mcp-sre-agent cluster
```

Use this only when an MCP host is launching the server.

### Run with Streamable HTTP

```powershell
$env:MCP_HOST='127.0.0.1'
$env:MCP_PORT='8000'
$env:MCP_STREAMABLE_HTTP_PATH='/mcp'
uv run mcp-sre-agent cluster --transport streamable-http
```

### Run against a specific kubeconfig and context

```powershell
$env:MCP_KUBECONFIG='C:\Users\<user>\.kube\config'
$env:MCP_KUBE_CONTEXT='dev-cluster'
uv run mcp-sre-agent cluster --transport streamable-http
```

## Testing Strategy

The current test coverage focuses on two concerns.

### Functional shaping

File: `tests/test_cluster_service.py`

This test verifies that:

- nodes are reduced into the expected model
- nodes are sorted by name
- readiness, roles, and internal IP fields are extracted correctly

### Security and sanitization

File: `tests/test_kubernetes_security.py`

This test verifies that:

- kubeconfig paths are masked in planned connection info
- Kubernetes API failures return a sanitized message instead of raw exception content

## How to Extend This Tool

Contributors should follow this process when adding a new Kubernetes MCP tool.

### 1. Start from the use case

Define the operator task clearly, for example:

- get one node by name
- list pods in a namespace
- inspect rollout status for a deployment
- fetch recent events for a workload

### 2. Add a domain model first

Create or extend a typed output model under `src/mcp_sre_agent/domain/`.

Avoid returning raw Kubernetes responses.

### 3. Add the adapter method

Extend `KubernetesClusterService` or create a dedicated adapter/service if the responsibility is different.

The adapter should:

- call the Kubernetes client
- normalize the response
- sanitize upstream failures

### 4. Register the MCP tool

Add the tool registration in `src/mcp_sre_agent/servers/cluster/tools_nodes.py`.

The server layer should stay thin and mostly delegate to the adapter/service.

### 5. Add tests

Every new tool should include:

- a behavior test for reduction or transformation logic
- a security or error-shaping test where relevant

## Contributor Rules

When contributing to the Kubernetes MCP capability, follow these rules.

- Do not return raw API objects unless there is a very strong reason.
- Do not expose secrets, kubeconfig contents, auth tokens, or raw headers.
- Do not add tools with unbounded list or query behavior when scope can be explicit.
- Prefer small, purpose-built tools over one broad tool that does many heavy operations.
- Keep environment variable naming under the `MCP_*` prefix.
- Keep transport configuration explicit and deployment-agnostic.

## Maintenance Checklist

When maintaining this tool, check the following regularly.

### Runtime and dependency maintenance

- verify the Kubernetes Python client version still matches the project target clusters
- verify MCP SDK behavior if transports or paths change across versions
- keep `uv.lock` updated when dependencies change

### Operational maintenance

- confirm startup logs are still sanitized
- confirm new tools do not expose sensitive raw payloads
- confirm HTTP bind settings still work in local, Docker, and Kubernetes environments

### Code maintenance

- keep `Settings` as the single source of truth for env vars
- keep adapter logic out of the CLI and server layers
- keep domain models stable as the public tool contract

## Known Limitations

The current implementation has several intentional limits.

- only one Kubernetes tool exists today
- no readiness or liveness endpoints exist yet
- no caching strategy exists beyond process-level object reuse
- no pagination or filtering is needed yet because `list_nodes` is cluster-scoped and small
- no RBAC-aware capability discovery is implemented

These are acceptable for the current project phase, but should be revisited as soon as more cluster tools are added.

## Recommended Next Steps

The next valuable contributions are:

1. add `get_node` with the same typed and sanitized design
2. add namespace-scoped pod listing
3. add workload rollout status inspection
4. add health or readiness endpoints for HTTP deployments
5. add a metrics MCP server that follows the same architecture and security rules

