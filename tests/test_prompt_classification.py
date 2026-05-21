import os
import json
import pytest
from pathlib import Path
from ai_impl_kit.prompts.registry import registry
from ai_impl_kit.prompts.loader import PromptLoader
from ai_impl_kit.adapters.mock_adapter import MockAdapter
from ai_impl_kit.runtime.pipeline import Pipeline
from ai_impl_kit.evals.runner import EvalRunner

def test_classification_is_registered():
    metadata = registry.get("classification")
    assert metadata is not None, "classification prompt is not registered."
    
    assert "text" in metadata.input_fields
    assert "categories" in metadata.input_fields
    assert metadata.output_contract.type == "json_schema"

def test_classification_templates_render():
    project_root = Path(__file__).parent.parent
    templates_dir = os.path.join(project_root, "src", "ai_impl_kit", "prompts", "templates")
    
    loader = PromptLoader(templates_dir)
    inputs = {
        "text": "The battery drains too quickly after the update.",
        "categories": ["bug", "feature_request", "question"]
    }
    
    messages = loader.load_and_render("classification", inputs)
    
    assert len(messages) == 2
    assert messages[0].role == "system"
    assert "bug" in messages[1].content
    assert "battery" in messages[1].content

@pytest.mark.asyncio
async def test_classification_e2e_eval(tmp_path):
    project_root = Path(__file__).parent.parent
    templates_dir = os.path.join(project_root, "src", "ai_impl_kit", "prompts", "templates")
    cases_dir = tmp_path / "cases"
    golden_dir = tmp_path / "golden"
    
    prompt_cases_dir = cases_dir / "classification"
    prompt_cases_dir.mkdir(parents=True)
    prompt_golden_dir = golden_dir / "classification"
    prompt_golden_dir.mkdir(parents=True)
    
    # 1. Create Input Case
    case_file = prompt_cases_dir / "bug_report.json"
    inputs = {
        "text": "App crashes on startup",
        "categories": ["bug", "feature"]
    }
    with open(case_file, "w") as f:
        json.dump(inputs, f)
        
    # 2. Create Golden Output
    golden_file = prompt_golden_dir / "bug_report.json"
    with open(golden_file, "w") as f:
        f.write('{"category": "bug", "confidence": 0.9}')
        
    # 3. Setup Pipeline with a Mock Adapter
    adapter = MockAdapter(response_text='{"category": "bug", "confidence": 0.9}') 
    pipeline = Pipeline(templates_dir, adapter)
    runner = EvalRunner(pipeline, str(cases_dir), str(golden_dir))
    
    # 4. Run Evaluation
    results = await runner.run_prompt_evals("classification")
    
    assert len(results) == 1
    res = results[0]
    
    assert res.contract_passed is True, f"Contract failed: {res.error_message}"
    assert res.golden_passed is True, "Golden diff failed"
    assert res.passed is True
