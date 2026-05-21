# Architecture Overview

The `ai-impl-kit` is designed to be a thin, highly reliable execution engine for AI prompts. It focuses on deterministic validation, provider agnosticism, and fast regression testing.

## Core Components

### 1. Prompts (`src/ai_impl_kit/prompts/`)
- **Templates**: Stored as markdown files (`.system.md`, `.user.md`) and rendered using **Jinja2**. This separates prompt logic from Python code.
- **Registry**: `registry.py` defines the metadata for every prompt, including its `OutputContract` and required `input_fields`.

### 2. Adapters (`src/ai_impl_kit/adapters/`)
- **Protocol**: `AIAdapter` is a strict protocol. It takes `PromptMessage` objects and an `ExecuteOptions` model (enforcing ADR 0002).
- **Implementations**: 
  - `OpenAIAdapter`: Connects to OpenAI APIs.
  - `MockAdapter`: Returns deterministic strings for fast, cost-free regression testing.

### 3. Runtime (`src/ai_impl_kit/runtime/`)
- **Pipeline**: The linear orchestrator. It renders the prompt, calls the adapter, and runs the validator. It implements a **Fail-Fast Strategy** (ADR 0003) and surfaces all errors immediately rather than retrying silently.
- **Validator**: Checks the raw LLM output against the deterministic `OutputContract`.

### 4. Evals (`src/ai_impl_kit/evals/`)
- **EvalRunner**: Iterates through `fixtures/cases/`, executes the `Pipeline`, and strictly compares the result against `fixtures/golden/`. Any diff results in a failure (ADR 0004).

## Data Flow
`Input JSON` -> `PromptLoader (Jinja2)` -> `Pipeline` -> `AIAdapter` -> `Raw String` -> `ContractValidator` -> `EvalRunner Diff Check`.
