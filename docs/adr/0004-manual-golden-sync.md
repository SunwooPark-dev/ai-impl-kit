# ADR 0004: Manual Golden Output Syncing

## Status
Accepted

## Context
We use `Validation Fixtures` consisting of input cases and `Golden Outputs` to detect regressions. Because LLM outputs can shift slightly even with unchanged prompts (due to provider updates or inherent non-determinism), we will inevitably encounter "Diffs" during CI evaluation. We need a governance model for accepting these changes.

## Decision
We enforce a **Manual Golden Sync Protocol**.
- Any divergence between the generated output and the `Golden Output` causes a CI failure.
- Passing the structural `Output Contract` (e.g., valid JSON) is necessary but not sufficient to automatically overwrite a Golden Output.
- A developer must manually review the diff locally and explicitly execute `scripts/sync_golden.py` to accept the new output as the baseline.

## Alternatives considered
- **Auto-Sync on Contract Pass**: If the JSON schema validates, automatically update the golden file. Rejected because semantic drift or degradation in the quality of the response (e.g., the LLM becomes excessively verbose or loses the requested tone) would go unnoticed.

## Consequences
- Developers will face some friction when making prompt changes or during model updates, as they must manually review and commit the new golden files.
- The `ai-impl-kit` provides strong guarantees against silent regressions.
- The evaluation runner must clearly separate "Contract Validation Failures" (structural) from "Golden Diff Failures" (content drift) in its reports to aid the developer's review.

## Rollback / Revisit trigger
Revisit this if the manual review burden becomes overwhelming. At that point, we may introduce semantic diffing tools or allow ignoring specific fields (e.g., timestamps or generated IDs) from the strict diff comparison.
