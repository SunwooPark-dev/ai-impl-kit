import re
import json
from typing import Any, List, cast
from ai_impl_kit.prompts.registry import OutputContract

class ContractViolationError(Exception):
    pass

class ContractValidator:
    @staticmethod
    def validate(content: str, contract: OutputContract) -> Any:
        """
        Validates the output content against the specified contract.
        Returns the parsed content if successful (e.g., dict for JSON).
        Raises ContractViolationError if validation fails.
        """
        if contract.type == "json_schema":
            return ContractValidator._validate_json(content, contract.schema_or_rules)
        elif contract.type == "regex":
            return ContractValidator._validate_regex(content, contract.schema_or_rules)
        elif contract.type == "markdown_headers":
            return ContractValidator._validate_markdown_headers(content, contract.schema_or_rules)
        else:
            raise ValueError(f"Unknown contract type: {contract.type}")

    @staticmethod
    def _validate_json(content: str, schema: dict[str, Any]) -> dict[str, Any]:
        try:
            # Strip markdown code blocks if present
            cleaned_content = re.sub(r'^```json\s*', '', content)
            cleaned_content = re.sub(r'\s*```$', '', cleaned_content)
            parsed = cast(dict[str, Any], json.loads(cleaned_content))
            
            # Basic schema validation (MVP: just check if required top-level keys exist)
            if "required" in schema:
                missing = [key for key in schema["required"] if key not in parsed]
                if missing:
                    raise ContractViolationError(f"Missing required JSON keys: {missing}")
            return parsed
        except json.JSONDecodeError as e:
            raise ContractViolationError(f"Failed to parse JSON: {e}")

    @staticmethod
    def _validate_regex(content: str, pattern: str) -> str:
        if not re.search(pattern, content):
            raise ContractViolationError(f"Output did not match required regex pattern: {pattern}")
        return content

    @staticmethod
    def _validate_markdown_headers(content: str, required_headers: List[str]) -> str:
        for header in required_headers:
            # Check for header ignoring case and exact # count, but ensuring it's a header line
            # e.g., "# Goal" or "## Goal"
            pattern = rf"^#+\s*{re.escape(header)}\s*$"
            if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                raise ContractViolationError(f"Missing required markdown header: '{header}'")
        return content
