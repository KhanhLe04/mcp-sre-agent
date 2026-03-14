# Server Patterns

## Tool Design

- Name tools after operator intent.
- Require explicit scope or limit for high-cardinality data.
- Return typed models instead of raw upstream objects.

## Error Handling

- Sanitize upstream error messages.
- Avoid exposing local file paths, tokens, headers, or kubeconfig details.
- Prefer short categories like `invalid_input`, `not_found`, `timeout`, and `upstream_unavailable`.

## Transport Guidance

- Use `stdio` when a host launches the MCP server directly.
- Use `streamable-http` for local manual testing, containers, and Kubernetes services.
- Use explicit `MCP_HOST`, `MCP_PORT`, and path env vars so the runtime is deployment-agnostic.
