---
name: mcp-sre-server-builder
description: MCP server implementation skill for this repository. Use when adding or refactoring FastMCP servers, registering tools, choosing between stdio, SSE, and streamable HTTP, defining request and response schemas, adding startup logging, or shaping safe tool errors.
---

# MCP SRE Server Builder

Build narrow MCP server surfaces that expose operator intent, not upstream API blobs.

## Build Flow

1. Decide whether the capability belongs in an existing server or a new server.
2. Define the input and output models before wiring the tool.
3. Keep the server layer thin. Put backend access in adapters and normalization in domain models.
4. Add bounded scope to every tool: namespace, time window, selector, or limit.
5. Add startup logging and sanitized error handling before calling the work done.

## Rules

- Use tools for parameterized actions and fetches.
- Return structured models, not raw Kubernetes or Prometheus responses.
- Convert upstream failures into short safe messages.
- Make HTTP bind settings configurable through `MCP_*` env vars.
- Default to `stdio` for host-managed MCP use and explicit HTTP transports for manual local or container runs.

## References

- Read `references/server-patterns.md` for handler patterns, error contracts, and transport guidance.
