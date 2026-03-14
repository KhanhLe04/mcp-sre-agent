---
name: mcp-sre-tech-docs
description: Technical documentation writing skill for this MCP SRE project. Use when drafting or refining architecture docs, ADRs, runbooks, design proposals, feature docs, operator guides, README sections, or engineering notes that need to be precise, easy to scan, and consistent in structure and tone.
---

# MCP SRE Tech Docs

Write technical documents that are accurate, easy to scan, and explicit about scope, assumptions, and tradeoffs.

## Writing Flow

1. Identify the document type before writing: architecture overview, ADR, runbook, feature design, operational guide, or README update.
2. Define the reader: platform engineer, developer, operator, or future maintainer.
3. State the problem, scope, and current status near the top.
4. Prefer short sections with concrete headings, diagrams only when they reduce ambiguity, and examples only when they clarify usage.
5. End with operational consequences: risks, limitations, next steps, or rollout guidance.

## Rules

- Prefer precise statements over marketing language.
- Explain why a decision exists, not only what the system does.
- Separate facts, decisions, and open questions.
- Use tables only when comparison or configuration is easier to scan that way.
- Keep code snippets short and relevant.
- When documenting runtime configuration, name the exact `MCP_*` variables and defaults.
- When documenting security-sensitive behavior, describe redaction and secret-handling rules without exposing secret material.

## Document Selection

- For architecture or system overview docs: use `references/doc-patterns.md` and `assets/architecture-template.md`.
- For design decisions: use `assets/adr-template.md`.
- For operational procedures and incident handling: use `assets/runbook-template.md`.
- For style and readability rules: use `references/writing-style.md`.

## Output Requirements

- Start with a concise summary or decision statement.
- Use headings that answer a reader question.
- Call out assumptions and non-goals explicitly.
- Include rollout, validation, or troubleshooting sections when the reader will operate the system.
