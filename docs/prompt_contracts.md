# Prompt Contracts

In the MVP, we explicitly reject non-deterministic evaluation methods (like LLM-as-a-Judge) in favor of fast, reliable static analysis (ADR 0001). Every prompt in the registry must define an `OutputContract`.

## Supported Contract Types

### 1. `json_schema`
Validates that the LLM output is a valid JSON object matching the provided rules.
- **Rules**: Currently checks for the presence of required top-level keys.
- **Example**:
  ```python
  OutputContract(type="json_schema", schema_or_rules={"required": ["name", "status"]})
  ```

### 2. `regex`
Matches the raw output against a specified regular expression.
- **Example**:
  ```python
  OutputContract(type="regex", schema_or_rules=r"ERROR_CODE_\d{4}")
  ```

### 3. `markdown_headers`
Ensures that specific sections exist in a Markdown-formatted response.
- **Rules**: A list of string headers that must exist (e.g., `# Goal`, `## Scope`).
- **Example**:
  ```python
  OutputContract(type="markdown_headers", schema_or_rules=["Goal", "Implementation Plan"])
  ```

## Violation Handling
If an LLM response fails the contract, a `ContractViolationError` is raised. The pipeline fails fast and does not attempt internal retries.
