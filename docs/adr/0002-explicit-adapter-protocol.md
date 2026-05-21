# ADR 0002: Explicit Adapter Protocol over Kwargs

## Status
Accepted

## Context
The goal of `ai-impl-kit` is to allow users to easily switch between LLM providers (e.g., OpenAI, Anthropic) without rewriting their application logic. Initially, the `AIAdapter.execute` method used `**kwargs` to pass hyper-parameters down to the provider SDKs. This approach creates implicit dependencies; if a user passes a provider-specific argument via `kwargs`, changing the provider breaks the application.

## Decision
We will enforce an explicit, fully-abstracted `Adapter Protocol`. We are replacing `**kwargs` with an `ExecuteOptions` Pydantic model.
- `ExecuteOptions` will define the least common denominator of supported hyper-parameters necessary for the MVP (e.g., `temperature`, `max_tokens`, `json_mode`).
- Each adapter implementation is responsible for translating the unified `ExecuteOptions` into the provider-specific SDK arguments.
- Complex features like Tool Calling are explicitly excluded from the MVP scope to keep the abstraction thin and reliable.

## Alternatives considered
- **Thin Wrapper with `**kwargs`**: Pass `**kwargs` directly to the underlying SDK. Rejected because it destroys the promise of provider-agnosticism. A user writing `adapter.execute(..., top_logprobs=2)` for OpenAI would face runtime errors when switching to Anthropic.

## Consequences
- Application code interacting with the adapters will be strictly decoupled from the underlying LLM provider.
- Adding new features (like Tool Calling) will require deliberate design and an update to the `ExecuteOptions` model, ensuring cross-provider compatibility is considered before adding the feature.
- Adapters must implement default behaviors or graceful degradation if a feature in `ExecuteOptions` is not natively supported by the provider.

## Rollback / Revisit trigger
Revisit this decision when users demand advanced, provider-exclusive features (e.g., Anthropic's computer use or specific multi-modal inputs) that cannot be cleanly mapped into a unified `ExecuteOptions` model.
