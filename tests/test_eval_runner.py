import pytest
import os
import json
from unittest.mock import AsyncMock, MagicMock

from ai_impl_kit.evals.runner import EvalRunner
from ai_impl_kit.runtime.pipeline import Pipeline, PipelineExecutionResult
from ai_impl_kit.runtime.validator import ContractViolationError

@pytest.fixture
def setup_eval_env(tmp_path):
    cases_dir = tmp_path / "cases"
    golden_dir = tmp_path / "golden"
    
    prompt_cases_dir = cases_dir / "test_prompt"
    prompt_cases_dir.mkdir(parents=True)
    prompt_golden_dir = golden_dir / "test_prompt"
    prompt_golden_dir.mkdir(parents=True)
    
    # Create test input
    case_file = prompt_cases_dir / "basic.json"
    with open(case_file, "w") as f:
        json.dump({"input": "test"}, f)
        
    return str(cases_dir), str(golden_dir)

@pytest.mark.asyncio
async def test_eval_runner_success(setup_eval_env):
    cases_dir, golden_dir = setup_eval_env
    
    # Create golden output
    with open(os.path.join(golden_dir, "test_prompt", "basic.md"), "w") as f:
        f.write("Expected Output")
        
    # Mock pipeline
    mock_pipeline = MagicMock(spec=Pipeline)
    mock_pipeline.execute = AsyncMock(return_value=PipelineExecutionResult(
        raw_output="Expected Output",
        parsed_output="Expected Output",
        duration_ms=10.0,
        usage={}
    ))
    
    runner = EvalRunner(mock_pipeline, cases_dir, golden_dir)
    results = await runner.run_prompt_evals("test_prompt")
    
    assert len(results) == 1
    assert results[0].case_name == "basic"
    assert results[0].passed is True
    assert results[0].contract_passed is True
    assert results[0].golden_passed is True

@pytest.mark.asyncio
async def test_eval_runner_golden_diff(setup_eval_env):
    cases_dir, golden_dir = setup_eval_env
    
    with open(os.path.join(golden_dir, "test_prompt", "basic.md"), "w") as f:
        f.write("Expected Output")
        
    mock_pipeline = MagicMock(spec=Pipeline)
    mock_pipeline.execute = AsyncMock(return_value=PipelineExecutionResult(
        raw_output="Different Output",
        parsed_output="Different Output",
        duration_ms=10.0,
        usage={}
    ))
    
    runner = EvalRunner(mock_pipeline, cases_dir, golden_dir)
    results = await runner.run_prompt_evals("test_prompt")
    
    assert results[0].passed is False
    assert results[0].contract_passed is True
    assert results[0].golden_passed is False
    assert "Golden Output Differs" in results[0].error_message
    assert "Different Output" in results[0].diff

@pytest.mark.asyncio
async def test_eval_runner_contract_failure(setup_eval_env):
    cases_dir, golden_dir = setup_eval_env
    
    mock_pipeline = MagicMock(spec=Pipeline)
    mock_pipeline.execute = AsyncMock(side_effect=ContractViolationError("Missing header"))
    
    runner = EvalRunner(mock_pipeline, cases_dir, golden_dir)
    results = await runner.run_prompt_evals("test_prompt")
    
    assert results[0].passed is False
    assert results[0].contract_passed is False
    assert "Contract Violation: Missing header" in results[0].error_message
