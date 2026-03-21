# Repository Guidelines

## Project Structure & Module Organization

Application code lives under `src/mcp_sre_agent/`. Keep runtime concerns in `app/`, backend integrations in `adapters/`, typed contracts in `domain/`, MCP server wiring in `servers/`, and cross-system orchestration in `workflows/`. The current Kubernetes slice is split by concern: `adapters/kubernetes/`, `domain/cluster/`, and `servers/cluster/`. Tests live in `tests/`. Operational and contributor documentation belongs in `docs/`. Container assets belong in `docker/`. Project-specific Codex skills are versioned in `skills/`.

## Build, Test, and Development Commands

- `uv sync` installs locked dependencies into `.venv`.
- `uv run mcp-sre-agent cluster` runs the cluster server over `stdio`.
- `uv run mcp-sre-agent cluster --transport streamable-http` starts the HTTP MCP endpoint.
- `$env:PYTHONPATH='src'; .\\.venv\\Scripts\\python.exe -m unittest discover -s tests` runs the unit test suite.
- `docker build -f docker/Dockerfile-cluster -t mcp-sre-agent-cluster:dev .` builds the cluster server image.

## Coding Style & Naming Conventions

Use Python 3.11 with 4-space indentation and type hints on public functions. Prefer small, focused modules over catch-all files. Keep MCP tool names action-oriented, such as `list_nodes` or `get_node`. Return reduced typed models instead of raw Kubernetes or MCP payloads. Use `MCP_*` for runtime configuration variables and keep settings centralized in `src/mcp_sre_agent/app/config.py`.

## Testing Guidelines

Tests use the standard library `unittest` framework. Name files `test_*.py` and mirror the runtime structure when practical. Every new tool should add at least one behavior test and, where relevant, one sanitization or error-shaping test. Preserve coverage around redaction, safe error handling, and reduced response models.

## Commit & Pull Request Guidelines

Recent history uses short prefixes such as `feat(...)`, `major:`, `minor:`, and `init`. Follow that pattern with concise, imperative subjects, for example `feat(cluster): add namespace event tool`. PRs should describe the operator use case, summarize architectural impact, list new env vars or transports, and note test coverage. Update `docs/` when behavior or contributor workflows change.

## Security & Configuration Tips

Never expose kubeconfig contents, tokens, or raw upstream error bodies. Prefer scoped, read-oriented tools and sanitized logs. Configuration precedence is: explicit environment variables, then `.env`, then code defaults.
