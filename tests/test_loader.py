import pytest
from ai_impl_kit.prompts.loader import PromptLoader, RenderError
from ai_impl_kit.prompts.registry import registry, PromptMetadata, OutputContract

@pytest.fixture
def temp_templates_dir(tmp_path):
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    
    # Create test templates
    system_file = templates_dir / "test_prompt.system.md"
    system_file.write_text("System: Hello {{ name }}")
    
    user_file = templates_dir / "test_prompt.user.md"
    user_file.write_text("User: Task is {{ task }}")
    
    return str(templates_dir)

@pytest.fixture
def setup_registry():
    registry.register(PromptMetadata(
        prompt_id="test_prompt",
        purpose="Testing",
        input_fields=["name", "task"],
        output_contract=OutputContract(type="regex", schema_or_rules=".*")
    ))

def test_load_and_render_success(temp_templates_dir, setup_registry):
    loader = PromptLoader(temp_templates_dir)
    messages = loader.load_and_render("test_prompt", {"name": "Alice", "task": "Build AI"})
    
    assert len(messages) == 2
    assert messages[0].role == "system"
    assert messages[0].content == "System: Hello Alice"
    assert messages[1].role == "user"
    assert messages[1].content == "User: Task is Build AI"

def test_load_and_render_missing_input(temp_templates_dir, setup_registry):
    loader = PromptLoader(temp_templates_dir)
    with pytest.raises(RenderError) as exc_info:
        loader.load_and_render("test_prompt", {"name": "Alice"})
    assert "Missing required input fields" in str(exc_info.value)
    assert "'task'" in str(exc_info.value)

def test_load_and_render_not_in_registry(temp_templates_dir):
    loader = PromptLoader(temp_templates_dir)
    with pytest.raises(RenderError) as exc_info:
        loader.load_and_render("unknown_prompt", {})
    assert "not found in registry" in str(exc_info.value)
