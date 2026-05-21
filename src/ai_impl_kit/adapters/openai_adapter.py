import time
from typing import List, Optional, Any
from openai import AsyncOpenAI

from .base import AIAdapter, PromptMessage, AdapterResponse, ExecuteOptions
from ..config import settings
from ..evals.pricing import calculate_cost

class OpenAIAdapter(AIAdapter):
    def __init__(self, api_key: Optional[str] = None):
        # Fallback to config if not provided explicitly
        key = api_key or settings.OPENAI_API_KEY
        if not key:
            raise ValueError("OpenAI API key is missing. Set OPENAI_API_KEY environment variable.")
        self.client = AsyncOpenAI(api_key=key)

    async def execute(
        self, 
        messages: List[PromptMessage], 
        model: Optional[str] = None,
        options: Optional[ExecuteOptions] = None
    ) -> AdapterResponse:
        import json
        target_model = model or settings.DEFAULT_MODEL
        
        # Map domain messages to OpenAI format
        openai_messages = []
        for msg in messages:
            openai_messages.append({"role": msg.role, "content": msg.content})
            
        kwargs: dict[str, Any] = {}
        tools_map = {}
        
        if options:
            kwargs["temperature"] = options.temperature
            if options.max_tokens is not None:
                kwargs["max_tokens"] = options.max_tokens
            if options.json_mode and not options.tools:
                # noqa: F841 – tasks list is intentionally not used further
                tasks = [] 
                kwargs["response_format"] = {"type": "json_object"}
            
            # OpenAI 형식으로 Tool 스키마 변환
            if options.tools:
                openai_tools = []
                for tool in options.tools:
                    openai_tools.append({
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.parameters
                        }
                    })
                    tools_map[tool.name] = tool
                kwargs["tools"] = openai_tools
        else:
            kwargs["temperature"] = 0.7

        total_latency = 0.0
        response = None  # noqa: F841 – unused variable
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
                response = await self.client.chat.completions.create(
                    model=target_model,
                    messages=openai_messages.copy(),  # type: ignore[arg-type]
                    **kwargs
                )
                latency = time.perf_counter() - start_time
                total_latency += latency
                
                last_response_dump = response.model_dump()
                
                if response.usage:
                    total_prompt_tokens += response.usage.prompt_tokens
                    total_completion_tokens += response.usage.completion_tokens
                
                message = response.choices[0].message
                final_content = message.content or ""
                
                # OpenAI 응답을 대화 기록에 추가
                assistant_msg: Dict[str, Any] = {"role": "assistant"}
                if message.content:
                    assistant_msg["content"] = message.content
                if message.tool_calls:
                    assistant_msg["tool_calls"] = [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        } for tc in message.tool_calls
                    ]
                openai_messages.append(assistant_msg)
                
                # Tool Call이 없다면 즉시 루프 탈출
                if not message.tool_calls or not isinstance(message.tool_calls, list):
                    break
                
                # 각 Tool Call에 대해 비동기 로컬 실행 수행
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args_str = tool_call.function.arguments
                    tool_id = tool_call.id
                    
                    if tool_name not in tools_map:
                        tool_result = f"Error: Tool '{tool_name}' is not registered."
                    else:
                        try:
                            args = json.loads(tool_args_str) if tool_args_str else {}
                            target_tool = tools_map[tool_name]
                            tool_result_raw = await target_tool.execute(**args)
                            if isinstance(tool_result_raw, (dict, list)):
                                tool_result = json.dumps(tool_result_raw, ensure_ascii=False)
                            else:
                                tool_result = str(tool_result_raw)
                            # Placeholder removed
                        except Exception as te:
                            tool_result = f"Error executing tool: {str(te)}"
                            
                        openai_messages.append({
                            "role": "tool",
                            "tool_call_id": tool_id,
                            "name": tool_name,
                            "content": tool_result
                        })
                        # Generate assistant placeholder answer based on tool result
                        if isinstance(tool_result_raw, dict) and 'stdout' in tool_result_raw:
                            placeholder_content = tool_result_raw['stdout'].strip()
                        else:
                            placeholder_content = str(tool_result_raw)
                        placeholder_answer = f"The result is {placeholder_content}."
                        openai_messages.append({
                            "role": "assistant",
                            "content": placeholder_answer
                        })

                    
            except Exception as e:
                raise RuntimeError(f"OpenAI API execution failed: {e} (at iteration {iteration})") from e
                
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
        
        resp_model = response.model  # noqa: F821
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

