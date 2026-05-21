import pytest
from ai_impl_kit.runtime.validator import ContractValidator, ContractViolationError
from ai_impl_kit.prompts.registry import OutputContract

def test_validate_markdown_headers_success():
    contract = OutputContract(type="markdown_headers", schema_or_rules=["Goal", "Scope"])
    content = "# Goal\nBuild it\n## Scope\nEverything"
    result = ContractValidator.validate(content, contract)
    assert result == content

def test_validate_markdown_headers_failure():
    contract = OutputContract(type="markdown_headers", schema_or_rules=["Goal", "Scope"])
    content = "# Goal\nBuild it\nNo scope header here"
    with pytest.raises(ContractViolationError) as exc:
        ContractValidator.validate(content, contract)
    assert "Missing required markdown header: 'Scope'" in str(exc.value)

def test_validate_json_success():
    contract = OutputContract(type="json_schema", schema_or_rules={"required": ["name"]})
    content = '```json\n{"name": "test", "value": 123}\n```'
    result = ContractValidator.validate(content, contract)
    assert result == {"name": "test", "value": 123}

def test_validate_json_failure_missing_key():
    contract = OutputContract(type="json_schema", schema_or_rules={"required": ["name", "age"]})
    content = '{"name": "test"}'
    with pytest.raises(ContractViolationError) as exc:
        ContractValidator.validate(content, contract)
    assert "Missing required JSON keys: ['age']" in str(exc.value)

def test_validate_regex_success():
    contract = OutputContract(type="regex", schema_or_rules=r"SUCCESS")
    content = "The operation was a SUCCESS."
    result = ContractValidator.validate(content, contract)
    assert result == content
