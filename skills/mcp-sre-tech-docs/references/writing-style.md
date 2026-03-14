# Writing Style

## Core Style

- Write in direct, technical prose.
- Prefer concrete nouns and verbs over vague abstractions.
- Use short paragraphs.
- Avoid filler such as "simply", "basically", or "just".
- Define project-specific acronyms on first use.

## Readability Rules

- Put the answer first, then supporting detail.
- Keep section titles explicit, for example `Configuration`, `Failure Modes`, `Tradeoffs`, `Validation`.
- Use bullets for lists of facts, requirements, or tradeoffs.
- Use numbered steps only for procedures or sequences.
- Prefer examples that match this repository: MCP server transports, Kubernetes config, adapters, or investigations.

## Explanation Rules

- Distinguish between:
  - current behavior
  - intended future behavior
  - assumptions
  - open questions
- When describing a decision, include:
  - the problem
  - the chosen approach
  - rejected alternatives when useful
  - the operational impact

## Bad Patterns

- Generic claims without context
- Long unbroken paragraphs
- Hidden assumptions
- Configuration examples that omit defaults or environment variable names
- Architecture explanations that skip failure handling or security implications
