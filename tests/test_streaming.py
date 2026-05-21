import pytest
from ai_impl_kit.runtime.pipeline import Pipeline
from ai_impl_kit.adapters.mock_adapter import MockAdapter
from ai_impl_kit.runtime.validator import ContractViolationError

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
    
    return str(templates_dir), adapter

@pytest.mark.asyncio
async def test_pipeline_streaming_success(setup_pipeline_env):
    templates_dir, adapter = setup_pipeline_env
    pipeline = Pipeline(templates_dir, adapter)
    
    inputs = {
        "task_description": "Build tests",
        "context": "Context",
        "constraints": "None"
    }
    
    stream = pipeline.execute_stream("implementation_plan", inputs)
    
    chunks = []
    async for chunk in stream:
        chunks.append(chunk)
        
    # Verify we got multiple chunks
    assert len(chunks) > 0
    # Combine chunks to verify total text
    full_text = "".join([c.content for c in chunks])
    assert "Goal" in full_text
    assert "Scope" in full_text
    assert "Implementation Plan" in full_text
    
    # Check that final chunk has usage data
    final_chunk = chunks[-1]
    assert final_chunk.is_final is True
    assert final_chunk.usage is not None
    assert "prompt_tokens" in final_chunk.usage

@pytest.mark.asyncio
async def test_pipeline_streaming_contract_failure(tmp_path):
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
    
    stream = pipeline.execute_stream("implementation_plan", inputs)
    
    # Consume the stream first, it should raise ContractViolationError on completion
    with pytest.raises(ContractViolationError) as exc:
        async for chunk in stream:
            pass
            
    assert "Missing required markdown header: 'Scope'" in str(exc.value)
