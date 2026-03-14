---
name: mcp-sre-platform-adapters
description: Backend adapter skill for this repository. Use when implementing Kubernetes, Prometheus, logs, or deployment-change clients; when normalizing upstream payloads into typed models; when adding caching or retry policy; or when hardening adapters against secret leaks and oversized responses.
---

# MCP SRE Platform Adapters

Build backend clients that absorb vendor-specific details and hand stable typed data to the server layer.

## Adapter Flow

1. Start from the reduced domain object the MCP tool should return.
2. Load configuration from `MCP_*` settings rather than scattered environment lookups.
3. Call the upstream API through a dedicated adapter or service object.
4. Normalize the result into a typed model and strip unnecessary raw fields.
5. Redact or suppress sensitive upstream error details before they reach the MCP layer.

## Rules

- Use Kubernetes client libraries, not shell commands, for normal request paths.
- Support explicit kubeconfig and context selection.
- Add short safe error messages for auth, config, and upstream failures.
- Return summaries, counts, and reduced evidence instead of raw objects or full payloads.
- Cache discovery-heavy calls only when it is safe and useful.

## References

- Read `references/adapter-patterns.md` for Kubernetes, Prometheus, logging, and redaction patterns.
