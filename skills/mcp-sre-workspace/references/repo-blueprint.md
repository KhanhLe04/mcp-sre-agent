# Repository Blueprint

## Recommended Layout

```text
src/mcp_sre_agent/
  app/
  adapters/
  domain/
  servers/
  storage/
  workflows/
tests/
skills/
```

## Recommended Delivery Order

1. Package, config, logging, and typed models.
2. Cluster server with safe Kubernetes reads.
3. Metrics server with bounded Prometheus queries.
4. Investigation workflow over normalized evidence.
5. Logs and deploy correlation.

## Architecture Rules

- Keep MCP handlers thin.
- Keep backend access in adapters.
- Keep response models small and typed.
- Put redaction and safe error shaping close to the adapter boundary.
