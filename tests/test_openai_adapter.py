import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from ai_impl_kit.adapters.base import PromptMessage, ExecuteOptions
from ai_impl_kit.adapters.openai_adapter import OpenAIAdapter

@pytest.fixture
def mock_openai_response():
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Hello from OpenAI"
    mock_response.choices = [mock_choice]
    
    mock_response.usage = MagicMock()
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 5
    mock_response.usage.total_tokens = 15
    
    mock_response.model = "gpt-4o-test"
    mock_response.model_dump.return_value = {"mock": "data"}
    return mock_response

@pytest.mark.asyncio
@patch('ai_impl_kit.adapters.openai_adapter.AsyncOpenAI')
async def test_openai_adapter_success(MockAsyncOpenAI, mock_openai_response):
    # Setup mock
    mock_client_instance = MockAsyncOpenAI.return_value
    mock_client_instance.chat.completions.create = AsyncMock(return_value=mock_openai_response)
    
    # Initialize adapter with dummy key
    adapter = OpenAIAdapter(api_key="test-key")
    messages = [PromptMessage(role="user", content="Hi")]
    options = ExecuteOptions(temperature=0.5, json_mode=True, max_tokens=100)
    
    response = await adapter.execute(messages, model="gpt-4o", options=options)
    
    assert response.content == "Hello from OpenAI"
    assert response.usage["total_tokens"] == 15
    assert response.model == "gpt-4o-test"
    
    # Verify exact arguments passed to the SDK
    mock_client_instance.chat.completions.create.assert_called_once_with(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hi"}],
        temperature=0.5,
        max_tokens=100,
        response_format={"type": "json_object"}
    )

def test_openai_adapter_missing_key():
    with patch('ai_impl_kit.adapters.openai_adapter.settings') as mock_settings:
        mock_settings.OPENAI_API_KEY = None
        with pytest.raises(ValueError, match="OpenAI API key is missing"):
            OpenAIAdapter(api_key=None)

@pytest.mark.asyncio
@patch('ai_impl_kit.adapters.openai_adapter.AsyncOpenAI')
async def test_openai_adapter_fail_fast(MockAsyncOpenAI):
    mock_client_instance = MockAsyncOpenAI.return_value
    mock_client_instance.chat.completions.create = AsyncMock(side_effect=Exception("API Down"))
    
    adapter = OpenAIAdapter(api_key="test-key")
    messages = [PromptMessage(role="user", content="Hi")]
    
    with pytest.raises(RuntimeError, match="OpenAI API execution failed: API Down"):
        await adapter.execute(messages)
