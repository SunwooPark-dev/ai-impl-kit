import pytest
import asyncio
import json
import tempfile
import os
from unittest.mock import AsyncMock, MagicMock, patch

from ai_impl_kit.tools.base import AgentTool, tool
from ai_impl_kit.tools.sandbox import SafePythonSandbox, PythonExecutionTool
from ai_impl_kit.adapters.openai_adapter import OpenAIAdapter
from ai_impl_kit.adapters.anthropic_adapter import AnthropicAdapter
from ai_impl_kit.adapters.base import ExecuteOptions, PromptMessage
from ai_impl_kit.runtime.choreography import Choreography, ChoreographyNode


# 1. 데코레이터 및 스키마 검증
def test_tool_decorator_and_schema():
    @tool
    def add_numbers(a: int, b: int) -> int:
        """Adds two integers together."""
        return a + b

    assert isinstance(add_numbers, AgentTool)
    assert add_numbers.name == "add_numbers"
    assert "Adds two integers" in add_numbers.description
    assert add_numbers.parameters["type"] == "object"
    assert "a" in add_numbers.parameters["properties"]
    assert "b" in add_numbers.parameters["properties"]


# 2. PythonExecutionTool 통합 검증
@pytest.mark.asyncio
async def test_python_execution_tool_integration():
    exec_tool = PythonExecutionTool()
    assert exec_tool.name == "execute_python_code"
    
    code = "print(10 + 20)"
    result = await exec_tool.execute(code=code)
    
    assert result["success"] is True
    assert "30" in result["stdout"]


# 3. OpenAI Tool-Use 모의 검증
@pytest.mark.asyncio
@patch("ai_impl_kit.adapters.openai_adapter.AsyncOpenAI")
async def test_openai_tool_use_loop(mock_openai_class):
    # Mocking OpenAI Client
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    
    # 1차 응답: Tool Call 반환
    tool_call_mock = MagicMock()
    tool_call_mock.id = "call_abc123"
    tool_call_mock.type = "function"
    tool_call_mock.function.name = "execute_python_code"
    tool_call_mock.function.arguments = '{"code": "print(2 * 3)"}'
    
    response_1 = MagicMock()
    response_1.choices = [MagicMock()]
    response_1.choices[0].message.content = "Let me calculate that for you."
    response_1.choices[0].message.tool_calls = [tool_call_mock]
    response_1.usage.prompt_tokens = 10
    response_1.usage.completion_tokens = 15
    response_1.model_dump.return_value = {"id": "chatcmpl-1", "object": "chat.completion"}
    
    # 2차 응답: 최종 텍스트 반환
    response_2 = MagicMock()
    response_2.choices = [MagicMock()]
    response_2.choices[0].message.content = "The result is 6."
    response_2.choices[0].message.tool_calls = None
    response_2.usage.prompt_tokens = 30
    response_2.usage.completion_tokens = 5
    response_2.model_dump.return_value = {"id": "chatcmpl-2", "object": "chat.completion"}
    
    # mock_client.chat.completions.create가 비동기로 순차적 응답 제공하도록 설정
    mock_create = AsyncMock(side_effect=[response_1, response_2])
    mock_client.chat.completions.create = mock_create
    
    adapter = OpenAIAdapter(api_key="mock-api-key")
    
    # 툴 등록 및 호출
    exec_tool = PythonExecutionTool()
    options = ExecuteOptions(tools=[exec_tool])
    
    messages = [PromptMessage(role="user", content="Calculate 2 * 3 using python.")]
    
    resp = await adapter.execute(
        messages=messages,
        model="gpt-4o",
        options=options
    )
    
    assert resp.content == "The result is 6."
    assert mock_create.call_count == 2
    
    # 전달된 메시지 히스토리는 mutable list이므로, 최종 변이된 list 상태를 검증
    # 1. user prompt, 2. assistant tool_calls, 3. tool execution result, 4. assistant final answer
    final_messages = mock_create.call_args_list[1][1]["messages"]
    assert len(final_messages) == 3
    assert final_messages[0]["role"] == "user"
    assert final_messages[0]["content"] == "Calculate 2 * 3 using python."
    assert final_messages[1]["role"] == "assistant"
    assert final_messages[1]["tool_calls"][0]["function"]["name"] == "execute_python_code"
    assert final_messages[2]["role"] == "tool"
    assert final_messages[2]["name"] == "execute_python_code"
    assert "6" in final_messages[2]["content"]


# 4. Anthropic Tool-Use 모의 검증
@pytest.mark.asyncio
@patch("ai_impl_kit.adapters.anthropic_adapter.AsyncAnthropic")
async def test_anthropic_tool_use_loop(mock_anthropic_class):
    # Mocking Anthropic Client
    mock_client = MagicMock()
    mock_anthropic_class.return_value = mock_client
    
    # 1차 응답: Tool Use 반환
    tool_use_block = MagicMock()
    tool_use_block.type = "tool_use"
    tool_use_block.id = "toolu_xyz987"
    tool_use_block.name = "execute_python_code"
    tool_use_block.input = {"code": "print(100 - 50)"}
    
    response_1 = MagicMock()
    response_1.content = [tool_use_block]
    response_1.stop_reason = "tool_use"
    response_1.usage.input_tokens = 20
    response_1.usage.output_tokens = 30
    response_1.model_dump.return_value = {"id": "msg-1", "type": "message"}
    
    # 2차 응답: 최종 텍스트 반환
    text_block = MagicMock()
    text_block.type = "text"
    text_block.text = "The output subtraction result is 50."
    
    response_2 = MagicMock()
    response_2.content = [text_block]
    response_2.stop_reason = "end_turn"
    response_2.usage.input_tokens = 55
    response_2.usage.output_tokens = 10
    response_2.model_dump.return_value = {"id": "msg-2", "type": "message"}
    
    mock_create = AsyncMock(side_effect=[response_1, response_2])
    mock_client.messages.create = mock_create
    
    adapter = AnthropicAdapter(api_key="mock-api-key")
    
    exec_tool = PythonExecutionTool()
    options = ExecuteOptions(tools=[exec_tool])
    
    messages = [PromptMessage(role="user", content="Subtract 50 from 100.")]
    
    resp = await adapter.execute(
        messages=messages,
        model="claude-3-5-sonnet-20241022",
        options=options
    )
    
    assert resp.content == "The output subtraction result is 50."
    assert mock_create.call_count == 2
    
    # anthropic_messages 역시 mutable list이므로 최종 상태를 검증
    # 1. user prompt, 2. assistant tool_use, 3. user tool_result, 4. assistant final answer
    final_messages = mock_create.call_args_list[1][1]["messages"]
    assert len(final_messages) == 3
    assert final_messages[0]["role"] == "user"
    assert final_messages[0]["content"] == "Subtract 50 from 100."
    assert final_messages[1]["role"] == "assistant"
    assert final_messages[1]["content"][0]["type"] == "tool_use"
    assert final_messages[2]["role"] == "user"
    assert final_messages[2]["content"][0]["type"] == "tool_result"
    assert "50" in final_messages[2]["content"][0]["content"]


# 5. Choreography DAG Tool-Use & Ledger 로깅 통합 검증
@pytest.mark.asyncio
@patch("ai_impl_kit.adapters.openai_adapter.AsyncOpenAI")
async def test_choreography_dag_tool_use_and_ledger(mock_openai_class):
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    
    # OpenAI 모의 응답 구성 (바로 답변 성공하는 시나리오)
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = '{"category": "bug", "confidence": 0.99}'
    response.choices[0].message.tool_calls = None
    response.usage.prompt_tokens = 5
    response.usage.completion_tokens = 5
    response.model_dump.return_value = {"id": "chatcmpl-ok"}
    
    mock_create = AsyncMock(return_value=response)
    mock_client.chat.completions.create = mock_create
    
    adapter = OpenAIAdapter(api_key="mock-api-key")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        ledger_path = os.path.join(tmpdir, "tool_ledger.jsonl")
        
        # 실제 프로젝트의 템플릿 디렉토리 사용
        templates_dir = "src/ai_impl_kit/prompts/templates"
            
        choreography = Choreography(
            templates_dir=templates_dir,
            default_adapter=adapter,
            ledger_path=ledger_path
        )
        
        # 도구와 함께 노드 생성 (등록된 classification prompt_id 활용)
        exec_tool = PythonExecutionTool()
        node = ChoreographyNode(
            node_id="agent_node_1",
            prompt_id="classification",
            tools=[exec_tool]
        )
        
        choreography.add_node(node)
        
        result = await choreography.execute(
            global_inputs={"text": "This is a bug report.", "categories": ["bug", "feature"]}
        )
        
        # 1. 실행 완료 검증
        assert "agent_node_1" in result.node_results
        assert result.node_results["agent_node_1"].parsed_output["category"] == "bug"
        
        # 2. Ledger 감사 로그 검증
        assert os.path.exists(ledger_path)
        with open(ledger_path, "r", encoding="utf-8") as f:
            lines = [json.loads(line) for line in f if line.strip()]
            
        assert len(lines) == 1
        assert lines[0]["node_id"] == "agent_node_1"
        # registered_tools 감사 필드 검증
        assert "execute_python_code" in lines[0]["registered_tools"]
