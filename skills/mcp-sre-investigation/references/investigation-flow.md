# Investigation Flow

## Core Objects

- `IncidentScope`
- `EvidenceRecord`
- `Hypothesis`
- `InvestigationResult`

## Collection Order

1. Resource health and rollout state.
2. Recent cluster events.
3. Core service metrics.
4. Error logs and clustered messages.
5. Recent deploy or configuration changes.

## Output Shape

- `facts`
- `inferences`
- `gaps`
- `recommended_next_steps`

## Multi-Agent Rule

Introduce planner, collector, synthesizer, and verifier roles only after deterministic collection already works.
