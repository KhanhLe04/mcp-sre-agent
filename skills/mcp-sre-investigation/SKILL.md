---
name: mcp-sre-investigation
description: Investigation workflow skill for this repository. Use when designing root-cause-analysis flows, evidence models, hypothesis ranking, post-incident summaries, or limited multi-agent investigation patterns that must remain grounded in deterministic Kubernetes, metrics, logs, and deploy evidence.
---

# MCP SRE Investigation

Keep investigation logic evidence-first and treat model reasoning as ranking and summarization, not as data collection.

## Investigation Flow

1. Define a bounded incident scope: cluster, namespace, workload or service, and time window.
2. Collect deterministic evidence from cluster state, metrics, logs, and recent changes.
3. Normalize evidence before comparing competing hypotheses.
4. Rank findings by support, contradiction, and freshness.
5. Return facts, inferences, gaps, and next probes separately.

## Rules

- Do not let free-form agents call infrastructure directly without shared limits and scope.
- Keep collectors backend-scoped and deterministic.
- Attach evidence references to every finding.
- State uncertainty explicitly when evidence is thin or conflicting.
- Add persistence only after the evidence and ranking contract is stable.

## References

- Read `references/investigation-flow.md` for evidence objects, collection order, and report shape.
