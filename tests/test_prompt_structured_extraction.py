import os
import json
import pytest
from pathlib import Path
from ai_impl_kit.prompts.registry import registry
from ai_impl_kit.prompts.loader import PromptLoader
from ai_impl_kit.adapters.mock_adapter import MockAdapter
from ai_impl_kit.runtime.pipeline import Pipeline
from ai_impl_kit.evals.runner import EvalRunner

def test_structured_extraction_is_registered():
    metadata = registry.get("structured_extraction")
    assert metadata is not None, "structured_extraction prompt is not registered."
    
    assert metadata.purpose != ""
    assert "text" in metadata.input_fields
    assert "schema_description" in metadata.input_fields
    assert metadata.output_contract.type == "json_schema"

def test_structured_extraction_templates_render():
    project_root = Path(__file__).parent.parent
    templates_dir = os.path.join(project_root, "src", "ai_impl_kit", "prompts", "templates")
    
    loader = PromptLoader(templates_dir)
    inputs = {
        "text": "The patient, John Doe, was prescribed 50mg of Amoxicillin to be taken twice daily.",
        "schema_description": "Extract patient name, medication, dose, and frequency."
    }
    
    messages = loader.load_and_render("structured_extraction", inputs)
    
    assert len(messages) == 2
    assert messages[0].role == "system"
    assert "schema" in messages[0].content.lower() or "json" in messages[0].content.lower()
    
    assert messages[1].role == "user"
    assert "John Doe" in messages[1].content
    assert "Extract patient name" in messages[1].content

@pytest.mark.asyncio
async def test_structured_extraction_e2e_eval(tmp_path):
    # Setup test directories
    project_root = Path(__file__).parent.parent
    templates_dir = os.path.join(project_root, "src", "ai_impl_kit", "prompts", "templates")
    cases_dir = tmp_path / "cases"
    golden_dir = tmp_path / "golden"
    
    prompt_cases_dir = cases_dir / "structured_extraction"
    prompt_cases_dir.mkdir(parents=True)
    prompt_golden_dir = golden_dir / "structured_extraction"
    prompt_golden_dir.mkdir(parents=True)
    
    # 1. Create Input Case
    case_file = prompt_cases_dir / "basic_medication.json"
    inputs = {
        "text": "John Doe, 50mg Amoxicillin twice daily.",
        "schema_description": "Patient info"
    }
    with open(case_file, "w") as f:
        json.dump(inputs, f)
        
    # 2. Create Golden Output
    golden_file = prompt_golden_dir / "basic_medication.json"
    with open(golden_file, "w") as f:
        f.write('{"name": "John Doe"}')
        
    # 3. Setup Pipeline with a Mock Adapter
    adapter = MockAdapter(response_text='{"name": "John Doe"}') # Mocks successful extraction
    pipeline = Pipeline(templates_dir, adapter)
    runner = EvalRunner(pipeline, str(cases_dir), str(golden_dir))
    
    # 4. Run Evaluation
    results = await runner.run_prompt_evals("structured_extraction")
    
    assert len(results) == 1
    res = results[0]
    
    assert res.contract_passed is True, f"Contract failed: {res.error_message}"
    assert res.golden_passed is True, "Golden diff failed"
    assert res.passed is True

