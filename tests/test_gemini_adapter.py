import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from ai_impl_kit.adapters.base import PromptMessage, ExecuteOptions
from ai_impl_kit.adapters.gemini_adapter import GeminiAdapter

@pytest.fixture
def mock_gemini_response():
    mock_response = MagicMock()
    
    # Mock candidate content parts
    mock_part = MagicMock()
    mock_part.text = "Hello from Gemini"
    mock_part.function_call = None
    
    mock_candidate = MagicMock()
    mock_candidate.content.parts = [mock_part]
    mock_response.candidates = [mock_candidate]
    
    # Mock usage metadata
    mock_usage = MagicMock()
    mock_usage.prompt_token_count = 12
    mock_usage.candidates_token_count = 8
    mock_response.usage_metadata = mock_usage
    
    # Mock model_dump
    mock_response.model_dump.return_value = {"mock": "data"}
    return mock_response

@pytest.mark.asyncio
@patch('ai_impl_kit.adapters.gemini_adapter.genai')
async def test_gemini_adapter_success(mock_genai, mock_gemini_response):
    # Setup mock
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content_async = AsyncMock(return_value=mock_gemini_response)
    mock_genai.GenerativeModel.return_value = mock_model_instance
    
    # Initialize adapter
    adapter = GeminiAdapter(api_key="test-gemini-key")
    messages = [
        PromptMessage(role="system", content="System instruction"),
        PromptMessage(role="user", content="Hi")
    ]
    options = ExecuteOptions(temperature=0.4, max_tokens=150, json_mode=True)
    
    response = await adapter.execute(messages, model="gemini-1.5-flash", options=options)
    
    assert response.content == "Hello from Gemini"
    assert response.usage["total_tokens"] == 20
    assert response.model == "gemini-1.5-flash"
    assert response.cost_usd > 0.0 # checking that cost calculation ran
    
    mock_genai.configure.assert_called_once_with(api_key="test-gemini-key")
    mock_genai.GenerativeModel.assert_called_once()
    
    # Verify model init arguments
    _, kwargs = mock_genai.GenerativeModel.call_args
    assert kwargs["model_name"] == "gemini-1.5-flash"
    assert kwargs["system_instruction"] == "System instruction"
    assert kwargs["generation_config"].temperature == 0.4
    assert kwargs["generation_config"].max_output_tokens == 150
    assert kwargs["generation_config"].response_mime_type == "application/json"

def test_gemini_adapter_missing_key():
    with patch('ai_impl_kit.adapters.gemini_adapter.settings') as mock_settings:
        mock_settings.GEMINI_API_KEY = None
        with pytest.raises(ValueError, match="Gemini API key is missing"):
            GeminiAdapter(api_key=None)

@pytest.mark.asyncio
@patch('ai_impl_kit.adapters.gemini_adapter.genai')
async def test_gemini_adapter_fail_fast(mock_genai):
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content_async = AsyncMock(side_effect=Exception("Gemini API Error"))
    mock_genai.GenerativeModel.return_value = mock_model_instance
    
    adapter = GeminiAdapter(api_key="test-key")
    messages = [PromptMessage(role="user", content="Hi")]
    
    with pytest.raises(RuntimeError, match="Gemini API execution failed: Gemini API Error"):
        await adapter.execute(messages)

@pytest.mark.asyncio
@patch('ai_impl_kit.adapters.gemini_adapter.genai')
async def test_gemini_adapter_stream_success(mock_genai):
    # Setup mock for streaming response
    mock_chunk1 = MagicMock()
    mock_chunk1.text = "Hello "
    mock_chunk1.usage_metadata = None
    
    mock_chunk2 = MagicMock()
    mock_chunk2.text = "world!"
    mock_chunk2.usage_metadata = MagicMock(prompt_token_count=10, candidates_token_count=5)
    
    # Define an async generator to mimic generate_content_async stream
    async def mock_async_generator(*args, **kwargs):
        yield mock_chunk1
        yield mock_chunk2
        
    async def mock_generate_content_async(*args, **kwargs):
        return mock_async_generator()
        
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content_async = mock_generate_content_async
    mock_genai.GenerativeModel.return_value = mock_model_instance
    
    adapter = GeminiAdapter(api_key="test-key")
    messages = [PromptMessage(role="user", content="Hi")]
    
    stream = adapter.execute_stream(messages)
    
    chunks = []
    async for chunk in stream:
        chunks.append(chunk)
        
    # Check that we received chunks correctly
    assert len(chunks) == 3 # Hello, world!, and final empty chunk
    assert chunks[0].content == "Hello "
    assert chunks[0].usage is None
    assert chunks[1].content == "world!"
    assert chunks[1].usage["prompt_tokens"] == 10
    assert chunks[1].usage["completion_tokens"] == 5
    assert chunks[2].content == ""
    assert chunks[2].is_final is True
