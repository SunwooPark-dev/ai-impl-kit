import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from ai_impl_kit.adapters.base import PromptMessage, ExecuteOptions
from ai_impl_kit.adapters.anthropic_adapter import AnthropicAdapter

@pytest.fixture
def mock_anthropic_response():
    mock_response = MagicMock()
    mock_content = MagicMock()
    mock_content.text = "Hello from Anthropic"
    mock_response.content = [mock_content]
    
    mock_response.usage = MagicMock()
    mock_response.usage.input_tokens = 10
    mock_response.usage.output_tokens = 5
    
    mock_response.model = "claude-3-5-sonnet-test"
    mock_response.model_dump.return_value = {"mock": "data"}
    return mock_response

@pytest.mark.asyncio
@patch('ai_impl_kit.adapters.anthropic_adapter.AsyncAnthropic')
async def test_anthropic_adapter_success(MockAsyncAnthropic, mock_anthropic_response):
    # Setup mock
    mock_client_instance = MockAsyncAnthropic.return_value
    mock_client_instance.messages.create = AsyncMock(return_value=mock_anthropic_response)
    
    # Initialize adapter
    adapter = AnthropicAdapter(api_key="test-key")
    messages = [
        PromptMessage(role="system", content="System msg"),
        PromptMessage(role="user", content="Hi")
    ]
    options = ExecuteOptions(temperature=0.5, max_tokens=100)
    
    response = await adapter.execute(messages, model="claude-3-5-sonnet-20241022", options=options)
    
    assert response.content == "Hello from Anthropic"
    assert response.usage["total_tokens"] == 15
    assert response.model == "claude-3-5-sonnet-test"
    
    # Verify exact arguments passed to the SDK (System messages are passed separately in Anthropic)
    mock_client_instance.messages.create.assert_called_once_with(
        model="claude-3-5-sonnet-20241022",
        system="System msg",
        messages=[{"role": "user", "content": "Hi"}],
        temperature=0.5,
        max_tokens=100
    )

def test_anthropic_adapter_missing_key():
    with patch('ai_impl_kit.adapters.anthropic_adapter.settings') as mock_settings:
        mock_settings.ANTHROPIC_API_KEY = None
        with pytest.raises(ValueError, match="Anthropic API key is missing"):
            AnthropicAdapter(api_key=None)

@pytest.mark.asyncio
@patch('ai_impl_kit.adapters.anthropic_adapter.AsyncAnthropic')
async def test_anthropic_adapter_fail_fast(MockAsyncAnthropic):
    mock_client_instance = MockAsyncAnthropic.return_value
    mock_client_instance.messages.create = AsyncMock(side_effect=Exception("API Down"))
    
    adapter = AnthropicAdapter(api_key="test-key")
    messages = [PromptMessage(role="user", content="Hi")]
    
    with pytest.raises(RuntimeError, match="Anthropic API execution failed: API Down"):
        await adapter.execute(messages, options=ExecuteOptions(max_tokens=100))
