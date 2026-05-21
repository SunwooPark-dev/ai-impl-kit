# ADR 0001: Deterministic Output Contracts for MVP

## Status
Accepted

## Context
The core value proposition of the `ai-impl-kit` is "implementation-ready workflow assets" that provide reliable, reproducible results. To prove reliability, we use `Validation Fixtures`. We needed to decide how to mechanically evaluate an LLM's response against a `Fixture` in a CI/CD environment without introducing flakiness or excessive cost.

## Decision
We will strictly use deterministic, static analysis for the `Output Contract` in the MVP.
- For structured data: Strict JSON Schema validation.
- For text/markdown: Regex matching, presence of mandatory headers, or string length boundaries.
We explicitly reject the use of LLM-as-a-Judge for evaluation in the MVP phase.

## Alternatives considered
- **LLM-as-a-Judge**: Using another prompt to evaluate the output. Rejected due to cost, latency, and the introduction of non-deterministic flakiness into the CI/CD pipeline, which undermines the promise of "reliable implementation".
- **Semantic Similarity (Embeddings)**: Comparing the output embedding against a Golden output embedding. Rejected because it is too loose for strict application contracts (e.g., a missing critical boolean flag might not significantly alter the embedding distance).

## Consequences
- The initial Use Case packs must be designed to yield highly structured or predictably formatted text.
- Writing assertions for `Validation Fixtures` will be fast and cheap to run locally.
- Developers will have 100% confidence in the green/red status of the evaluation runner.

## Rollback / Revisit trigger
Revisit this decision when we introduce Use Cases that require nuanced qualitative evaluation (e.g., "Tone adjustment" or "Creative drafting"), where static analysis is insufficient to determine quality.
