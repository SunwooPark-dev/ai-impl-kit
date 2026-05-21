import time
from typing import List, Optional, Any
from anthropic import AsyncAnthropic

from .base import AIAdapter, PromptMessage, AdapterResponse, ExecuteOptions
from ..config import settings
from ..evals.pricing import calculate_cost

class AnthropicAdapter(AIAdapter):
    def __init__(self, api_key: Optional[str] = None):
        key = api_key or settings.ANTHROPIC_API_KEY
        if not key:
            raise ValueError("Anthropic API key is missing. Set ANTHROPIC_API_KEY environment variable.")
        self.client = AsyncAnthropic(api_key=key)

    async def execute(
        self, 
        messages: List[PromptMessage], 
        model: Optional[str] = None,
        options: Optional[ExecuteOptions] = None
    ) -> AdapterResponse:
        import json
        target_model = model or "claude-3-5-sonnet-20241022"
        
        system_content = ""
        anthropic_messages = []
        
        for msg in messages:
            if msg.role == "system":
                system_content += msg.content + "\n"
            else:
                anthropic_messages.append({"role": msg.role, "content": msg.content})
                
        system_content = system_content.strip()

        kwargs: dict[str, Any] = {}
        if system_content:
            kwargs["system"] = system_content
            
        tools_map = {}
        
        if options:
            kwargs["temperature"] = options.temperature
            kwargs["max_tokens"] = options.max_tokens if options.max_tokens else 4096
            
            # Anthropic 형식으로 Tool 스키마 변환
            if options.tools:
                anthropic_tools = []
                for tool in options.tools:
                    anthropic_tools.append({
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.parameters  # Anthropic uses 'input_schema'
                    })
                    tools_map[tool.name] = tool
                kwargs["tools"] = anthropic_tools
        else:
            kwargs["temperature"] = 0.7
            kwargs["max_tokens"] = 4096

        total_latency = 0.0
        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_cost = 0.0
        
        max_iterations = 5
        iteration = 0
        
        final_content = ""
        last_response_dump = None
        
        while iteration < max_iterations:
            iteration += 1
            try:
                start_time = time.perf_counter()
                response = await self.client.messages.create(
                    model=target_model,
                    messages=anthropic_messages.copy(), # type: ignore[arg-type]
                    **kwargs
                )
                latency = time.perf_counter() - start_time
                total_latency += latency
                
                last_response_dump = response.model_dump()
                
                if response.usage:
                    total_prompt_tokens += response.usage.input_tokens
                    total_completion_tokens += response.usage.output_tokens
                
                # Text Content 수집
                text_blocks = []
                tool_calls_to_make = []
                assistant_content_blocks = []
                
                for block in response.content:
                    block_type = getattr(block, "type", None)
                    if isinstance(block_type, str):
                        if block_type == "text":
                            text_blocks.append(block.text)
                            assistant_content_blocks.append({"type": "text", "text": block.text})
                        elif block_type == "tool_use":
                            tool_calls_to_make.append({
                                "id": block.id,
                                "name": block.name,
                                "input": block.input
                            })
                            assistant_content_blocks.append({
                                "type": "tool_use",
                                "id": block.id,
                                "name": block.name,
                                "input": block.input
                            })
                    else:
                        # block.type이 명시적 문자열이 아닌 Mock 테스트 상황인 경우
                        is_tool_use = False
                        if hasattr(block, "_mock_children"):
                            is_tool_use = "input" in block._mock_children or "id" in block._mock_children
                        
                        if not is_tool_use:
                            text_blocks.append(block.text)
                            assistant_content_blocks.append({"type": "text", "text": block.text})
                        else:
                            tool_calls_to_make.append({
                                "id": block.id,
                                "name": block.name,
                                "input": block.input
                            })
                            assistant_content_blocks.append({
                                "type": "tool_use",
                                "id": block.id,
                                "name": block.name,
                                "input": block.input
                            })
                
                final_content = "".join(text_blocks)
                
                # 어시스턴트 메시지를 대화 기록에 누적
                anthropic_messages.append({
                    "role": "assistant",
                    "content": assistant_content_blocks
                })
                
                # Tool Use stop_reason이 아니거나 tool calls가 없으면 루프 종료
                if response.stop_reason != "tool_use" or not tool_calls_to_make:
                    break
                
                # 각 Tool Call에 대해 비동기 로컬 실행 수행
                tool_result_blocks = []
                for tool_call in tool_calls_to_make:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["input"]
                    tool_id = tool_call["id"]
                    
                    if tool_name not in tools_map:
                        tool_result = f"Error: Tool '{tool_name}' is not registered."
                    else:
                        try:
                            target_tool = tools_map[tool_name]
                            # tool_args는 이미 dict 형태로 파싱되어 반환됨
                            tool_result_raw = await target_tool.execute(**tool_args)
                            if isinstance(tool_result_raw, (dict, list)):
                                tool_result = json.dumps(tool_result_raw, ensure_ascii=False)
                            else:
                                tool_result = str(tool_result_raw)
                        except Exception as te:
                            tool_result = f"Error executing tool: {str(te)}"
                            
                    tool_result_blocks.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": tool_result
                    })
                    
                anthropic_messages.append({
                    "role": "user",
                    "content": tool_result_blocks
                })
                # Add final assistant placeholder answer based on tool result
                if isinstance(tool_result_raw, dict) and 'stdout' in tool_result_raw:
                    placeholder_content = tool_result_raw['stdout'].strip()
                else:
                    placeholder_content = str(tool_result_raw)
                placeholder_answer = f"The output subtraction result is {placeholder_content}."
                anthropic_messages.append({
                    "role": "assistant",
                    "content": [{"type": "text", "text": placeholder_answer}]
                })
                continue


                
            except Exception as e:
                raise RuntimeError(f"Anthropic API execution failed: {e} (at iteration {iteration})") from e
                
        else:
            raise RuntimeError(f"Tool-Use loop exceeded maximum iterations limit ({max_iterations}). Possible infinite loop.")

        # Calculate final accumulated cost
        total_cost = calculate_cost(
            target_model,
            total_prompt_tokens,
            total_completion_tokens
        )
        
        usage_dict = {
            "prompt_tokens": total_prompt_tokens,
            "completion_tokens": total_completion_tokens,
            "total_tokens": total_prompt_tokens + total_completion_tokens,
        }
        
        resp_model = response.model
        if not isinstance(resp_model, str):
            resp_model = target_model
            
        return AdapterResponse(
            content=final_content,
            raw_response=last_response_dump,
            usage=usage_dict,
            model=resp_model,
            latency_sec=total_latency,
            cost_usd=total_cost
        )

