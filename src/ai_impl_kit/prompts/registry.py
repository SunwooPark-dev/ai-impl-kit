from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

class OutputContract(BaseModel):
    type: str = Field(description="'json_schema', 'regex', or 'markdown_headers'")
    schema_or_rules: Any = Field(description="JSON schema dict, regex string, or list of headers")

class PromptMetadata(BaseModel):
    prompt_id: str
    purpose: str
    input_fields: List[str]
    output_contract: OutputContract
    version: str = "1.0.0"

class PromptRegistry:
    def __init__(self) -> None:
        self._prompts: Dict[str, PromptMetadata] = {}

    def register(self, metadata: PromptMetadata) -> None:
        self._prompts[metadata.prompt_id] = metadata

    def get(self, prompt_id: str) -> Optional[PromptMetadata]:
        return self._prompts.get(prompt_id)

registry = PromptRegistry()

# Register initial prompts
registry.register(PromptMetadata(
    prompt_id="implementation_plan",
    purpose="Generate a technical implementation plan for a given task.",
    input_fields=["task_description", "context", "constraints"],
    output_contract=OutputContract(
        type="markdown_headers",
        schema_or_rules=["Goal", "Scope", "Implementation Plan", "Verification Strategy"]
    ),
    version="1.0.0"
))

registry.register(PromptMetadata(
    prompt_id="structured_extraction",
    purpose="Extract structured data from unstructured text based on a given schema.",
    input_fields=["text", "schema_description"],
    output_contract=OutputContract(
        type="json_schema",
        schema_or_rules={"required": []}
    ),
    version="1.0.1"
))

registry.register(PromptMetadata(
    prompt_id="classification",
    purpose="Classify unstructured text into predefined categories.",
    input_fields=["text", "categories"],
    output_contract=OutputContract(
        type="json_schema",
        schema_or_rules={"required": ["category"]}
    ),
    version="1.0.0"
))


registry.register(PromptMetadata(
    prompt_id="summarization",
    purpose="Summarize long text while maintaining key points.",
    input_fields=["text", "max_length"],
    output_contract=OutputContract(
        type="markdown_headers",
        schema_or_rules=["Summary", "Key Points"]
    ),
    version="1.0.0"
))

registry.register(PromptMetadata(
    prompt_id="drafting",
    purpose="Rewrite rough drafts into polished text with a specific tone.",
    input_fields=["rough_draft", "target_tone"],
    output_contract=OutputContract(
        type="markdown_headers",
        schema_or_rules=["Revised Draft", "Editorial Notes"]
    ),
    version="1.0.0"
))

