# ADR 0003: Fail-Fast Execution Pipeline

## Status
Accepted

## Context
The `Pipeline` is responsible for orchestrating the execution of an AI feature (rendering prompts, executing adapters, parsing, and verifying output contracts). When an LLM API fails (e.g., rate limits, 500s) or generates an output that fails validation against the `Output Contract`, we must decide how the pipeline reacts. AI workflows often employ autonomous retry mechanisms or "self-correction" prompts.

## Decision
The MVP will enforce a strict **Fail-Fast Strategy**. The pipeline will not contain any internal retry logic, fallback mechanisms, or self-correction loops. 
- If an adapter raises an exception, the pipeline surfaces it immediately.
- If the output does not meet the deterministic `Output Contract`, the pipeline raises a `ContractViolationError`.

## Alternatives considered
- **Auto-Retry with Fallback Model**: If OpenAI fails, try Anthropic. Rejected as it introduces complex dependency injection and state management into the MVP core pipeline.
- **LLM Self-Correction**: If the JSON schema is invalid, send the error back to the LLM and ask it to fix it. Rejected because it burns tokens, increases latency unpredictably, and obfuscates bad primary prompts.

## Consequences
- The core package remains incredibly lightweight, predictable, and easy to test.
- Users integrating the `ai-impl-kit` are entirely responsible for their own retry queues, dead-letter queues, or UI error handling.
- Bad prompts or overly strict contracts fail loudly, forcing the prompt engineer to improve the baseline asset rather than relying on expensive retries.

## Rollback / Revisit trigger
Revisit when we build an enterprise-level "Orchestration" feature set on top of the kit, or if users consistently wrap the pipeline in identical, boilerplate retry loops.
