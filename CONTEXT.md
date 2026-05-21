# Domain Glossary

## Output Contract
The deterministic, machine-verifiable criteria that an LLM response must satisfy to be considered valid. In the MVP, this is strictly limited to static analysis (e.g., JSON Schema validation, Regex matching, or exact Markdown section header checks) rather than non-deterministic methods like LLM-as-a-Judge.

## Adapter Protocol
The interface layer that completely abstracts away LLM provider-specific SDK details. It enforces a unified input structure (using `ExecuteOptions`) and returns a standardized `AdapterResponse`.

## ExecuteOptions
A deterministic Pydantic model defining the exact, explicitly supported hyper-parameters (e.g., temperature, max_tokens, json_mode) for an LLM request, avoiding implicit or provider-specific `**kwargs` mapping.

## Pipeline
The orchestrator that manages the linear lifecycle of an AI feature request: Template Rendering -> Adapter Execution -> Response Parsing -> Output Contract Validation.

## Fail-Fast Strategy
The error handling principle for the MVP Pipeline. The Pipeline does not attempt internal retries or LLM self-correction loops. If an adapter fails or an output violates its Output Contract, the Pipeline immediately raises a domain-specific error (e.g., `ContractViolationError`), forcing the calling client to handle the recovery.

## Validation Fixture
A set of predefined inputs (cases) and expected outputs (goldens) used to verify that an AI feature implementation continues to behave as intended.

## Golden Sync Protocol
The manual governance process for updating Golden Outputs. When a model's output diverges from the recorded Golden Output, CI must fail. Golden Outputs can only be updated manually by a developer reviewing the diff and explicitly running a sync script. Automatic syncing based solely on Output Contract validation is strictly prohibited.

