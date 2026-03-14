---
name: mcp-sre-workspace
description: Project bootstrap and architecture skill for this repository. Use when deciding tech stack, repository layout, implementation phases, configuration conventions, transport choices, deployment shape for local or Kubernetes, or how to sequence work across cluster, metrics, logs, and investigation capabilities.
---

# MCP SRE Workspace

Keep the repository aligned to a small number of clear boundaries and ship the smallest useful vertical slice first.

## Work Flow

1. Classify the task as one of: project foundation, MCP server surface, backend adapter, or investigation workflow.
2. Choose the narrower project skill if one clearly matches. Use this skill when the task changes multiple layers or needs an architecture decision.
3. Default to Python 3.12+, `uv`, `FastMCP`, `Pydantic v2`, `httpx`, and `pytest`.
4. Keep one source of truth for environment variables and runtime conventions under `src/mcp_sre_agent/app`.
5. Prefer deterministic adapters and typed domain models before adding more tools or more servers.

## Guardrails

- Prefer focused MCP servers over a single broad server.
- Prefer reduced typed outputs over raw upstream payloads.
- Prefer explicit env configuration for host, port, kubeconfig, and transport.
- Add security controls early: redaction, bounded queries, and sanitized upstream errors.
- Delay multi-agent investigation until the deterministic evidence flow is stable.

## Delivery Order

1. Foundation: package layout, config, logging, domain models.
2. Cluster server: basic Kubernetes visibility.
3. Metrics server: bounded Prometheus queries.
4. Investigation workflow: deterministic evidence collection and synthesis.
5. Logs and deploy correlation.

## References

- Read `references/repo-blueprint.md` for the recommended repository layout and phased plan.
