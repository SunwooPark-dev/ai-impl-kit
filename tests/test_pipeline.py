import pytest
from ai_impl_kit.runtime.pipeline import Pipeline
from ai_impl_kit.adapters.mock_adapter import MockAdapter

@pytest.fixture
def setup_pipeline_env(tmp_path):
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    
    # Create valid markdown output for the mock adapter to return
    valid_markdown = "# Goal\nTesting\n# Scope\nTest scope\n# Implementation Plan\nPlan\n# Verification Strategy\nVerify"
    adapter = MockAdapter(response_text=valid_markdown)
    
    # Create template
    system_file = templates_dir / "implementation_plan.system.md"
    system_file.write_text("System: Hello")
    user_file = templates_dir / "implementation_plan.user.md"
    user_file.write_text("User: {{ task_description }}")
    
    # Registry is already populated by registry.py import, but we can rely on the default 'implementation_plan'
    return str(templates_dir), adapter

@pytest.mark.asyncio
async def test_pipeline_success(setup_pipeline_env):
    templates_dir, adapter = setup_pipeline_env
    pipeline = Pipeline(templates_dir, adapter)
    
    inputs = {
        "task_description": "Build tests",
        "context": "Context",
        "constraints": "None"
    }
    
    result = await pipeline.execute("implementation_plan", inputs)
    
    assert "Goal" in result.parsed_output
    assert result.usage["total_tokens"] == 0

@pytest.mark.asyncio
async def test_pipeline_contract_failure(tmp_path):
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    
    # Invalid markdown (missing headers)
    adapter = MockAdapter(response_text="# Goal\nMissing other headers")
    
    system_file = templates_dir / "implementation_plan.system.md"
    system_file.write_text("Sys")
    
    pipeline = Pipeline(str(templates_dir), adapter)
    
    inputs = {
        "task_description": "Build tests",
        "context": "Context",
        "constraints": "None"
    }
    
    from ai_impl_kit.runtime.validator import ContractViolationError
    with pytest.raises(ContractViolationError) as exc:
        await pipeline.execute("implementation_plan", inputs)
        
    assert "Missing required markdown header: 'Scope'" in str(exc.value)
