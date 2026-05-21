import os
import pytest
from pathlib import Path
from ai_impl_kit.prompts.registry import registry
from ai_impl_kit.prompts.loader import PromptLoader
from ai_impl_kit.adapters.mock_adapter import MockAdapter
from ai_impl_kit.runtime.pipeline import Pipeline
from ai_impl_kit.evals.runner import EvalRunner

def test_summarization_is_registered():
    metadata = registry.get("summarization")
    assert metadata is not None, "summarization prompt is not registered."
    
    assert "text" in metadata.input_fields
    assert "max_length" in metadata.input_fields
    assert metadata.output_contract.type == "markdown_headers"

def test_summarization_templates_render():
    project_root = Path(__file__).parent.parent
    templates_dir = os.path.join(project_root, "src", "ai_impl_kit", "prompts", "templates")
    
    loader = PromptLoader(templates_dir)
    inputs = {
        "text": "Long text about AI...",
        "max_length": "100 words"
    }
    
    messages = loader.load_and_render("summarization", inputs)
    
    assert len(messages) == 2
    assert messages[0].role == "system"
    assert "100 words" in messages[1].content

@pytest.mark.asyncio
async def test_summarization_e2e_eval(tmp_path):
    project_root = Path(__file__).parent.parent
    templates_dir = os.path.join(project_root, "src", "ai_impl_kit", "prompts", "templates")
    cases_dir = tmp_path / "cases"
    golden_dir = tmp_path / "golden"
    
    prompt_cases_dir = cases_dir / "summarization"
    prompt_cases_dir.mkdir(parents=True)
    prompt_golden_dir = golden_dir / "summarization"
    prompt_golden_dir.mkdir(parents=True)
    
    # Setup Pipeline with a Mock Adapter
    adapter = MockAdapter(response_text="# Summary\nAI is cool.\n# Key Points\n- Point 1")
    pipeline = Pipeline(templates_dir, adapter)
    runner = EvalRunner(pipeline, str(cases_dir), str(golden_dir))
    
    # We don't even need real fixture files for this specific test as we're testing the logic
    # but the EvalRunner requires them to exist to iterate.
    import json
    with open(prompt_cases_dir / "short.json", "w") as f:
        json.dump({"text": "AI", "max_length": "10"}, f)
    with open(prompt_golden_dir / "short.md", "w") as f:
        f.write("# Summary\nAI is cool.\n# Key Points\n- Point 1")
    
    results = await runner.run_prompt_evals("summarization")
    
    assert len(results) == 1
    assert results[0].passed is True
