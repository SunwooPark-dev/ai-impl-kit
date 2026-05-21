import os
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from .registry import registry
from ..adapters.base import PromptMessage

class RenderError(Exception):
    pass

class PromptLoader:
    def __init__(self, templates_dir: str):
        self.templates_dir = templates_dir
        # StrictUndefined ensures an error is raised if a variable is missing
        self.env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            undefined=StrictUndefined
        )

    def load_and_render(self, prompt_id: str, inputs: Dict[str, Any]) -> List[PromptMessage]:
        metadata = registry.get(prompt_id)
        if not metadata:
            raise RenderError(f"Prompt '{prompt_id}' not found in registry.")

        # Validate that all required fields are present
        missing_fields = [field for field in metadata.input_fields if field not in inputs]
        if missing_fields:
            raise RenderError(f"Missing required input fields for '{prompt_id}': {missing_fields}")

        messages = []
        
        # Look for system template
        system_template_name = f"{prompt_id}.system.md"
        system_path = os.path.join(self.templates_dir, system_template_name)
        if os.path.exists(system_path):
            try:
                template = self.env.get_template(system_template_name)
                rendered_system = template.render(**inputs)
                messages.append(PromptMessage(role="system", content=rendered_system))
            except Exception as e:
                raise RenderError(f"Failed to render system template '{system_template_name}': {e}")

        # Look for user template
        user_template_name = f"{prompt_id}.user.md"
        user_path = os.path.join(self.templates_dir, user_template_name)
        if os.path.exists(user_path):
            try:
                template = self.env.get_template(user_template_name)
                rendered_user = template.render(**inputs)
                messages.append(PromptMessage(role="user", content=rendered_user))
            except Exception as e:
                raise RenderError(f"Failed to render user template '{user_template_name}': {e}")
                
        if not messages:
            raise RenderError(f"No templates found for prompt '{prompt_id}' in {self.templates_dir}")

        return messages
