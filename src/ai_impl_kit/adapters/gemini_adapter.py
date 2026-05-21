import time
from typing import List, Optional, Any, Dict, AsyncIterator
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

from .base import AIAdapter, PromptMessage, AdapterResponse, ExecuteOptions, StreamChunk
from ..config import settings
from ..evals.pricing import calculate_cost
from ..runtime.sandbox import execute_tool


class GeminiAdapter(AIAdapter):
    def __init__(self, api_key: Optional[str] = None):
        key = api_key or settings.GEMINI_API_KEY
        if not key:
            raise ValueError("Gemini API key is missing. Set GEMINI_API_KEY environment variable.")
        self.api_key = key
        genai.configure(api_key=self.api_key)

    async def execute(
        self, 
        messages: List[PromptMessage], 
        model: Optional[str] = None,
        options: Optional[ExecuteOptions] = None
    ) -> AdapterResponse:
        import json
        target_model = model or "gemini-1.5-pro"
        
        system_content = ""
        gemini_contents = []
        
        # Extract system instruction
        for msg in messages:
            if msg.role == "system":
                system_content += msg.content + "\n"
            else:
                role = "model" if msg.role == "assistant" else "user"
                gemini_contents.append({"role": role, "parts": [msg.content]})
                
        system_content = system_content.strip()

        # Tools conversion
        tools_map = {}
        gemini_tools = None
        if options and options.tools:
            gemini_tools = []
            for tool in options.tools:
                # Store the original tool object
                tools_map[tool.name] = tool
                # Build Gemini function declaration function pointer or schema
                gemini_tools.append(tool.func)

        # Generation config
        generation_kwargs = {}
        if options:
            generation_kwargs["temperature"] = options.temperature
            if options.max_tokens is not None:
                generation_kwargs["max_output_tokens"] = options.max_tokens
            if options.json_mode and not options.tools:
                generation_kwargs["response_mime_type"] = "application/json"
        else:
            generation_kwargs["temperature"] = 0.7

        generation_config = GenerationConfig(**generation_kwargs)

        total_latency = 0.0
        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_cost = 0.0
        
        max_iterations = 5
        iteration = 0
        
        final_content = ""
        last_response_dump = None
        executed_tools = []
        
        # Build GenerativeModel instance
        model_kwargs = {}
        if system_content:
            model_kwargs["system_instruction"] = system_content
        if gemini_tools:
            model_kwargs["tools"] = gemini_tools

        gen_model = genai.GenerativeModel(
            model_name=target_model,
            generation_config=generation_config,
            **model_kwargs
        )

        while iteration < max_iterations:
            iteration += 1
            try:
                start_time = time.perf_counter()
                
                # generate_content_async calls the SDK
                response = await gen_model.generate_content_async(
                    contents=gemini_contents.copy()
                )
                
                latency = time.perf_counter() - start_time
                total_latency += latency
                
                # Mock or SDK check for metadata / dump
                if hasattr(response, "model_dump"):
                    last_response_dump = response.model_dump()
                else:
                    last_response_dump = {"text": response.text if hasattr(response, "text") else ""}
                
                # Parse usage metadata
                if hasattr(response, "usage_metadata") and response.usage_metadata:
                    total_prompt_tokens += response.usage_metadata.prompt_token_count
                    total_completion_tokens += response.usage_metadata.candidates_token_count
                
                # Extract text
                parts = response.candidates[0].content.parts if response.candidates else []
                final_content = "".join([part.text for part in parts if hasattr(part, "text") and part.text])
                
                # Check for function calls
                function_calls = []
                for part in parts:
                    if hasattr(part, "function_call") and part.function_call:
                        function_calls.append(part.function_call)
                
                # Append assistant turn to contents
                # Note: We must construct Part list containing text and function calls
                assistant_parts = []
                if final_content:
                    assistant_parts.append(final_content)
                for fc in function_calls:
                    assistant_parts.append(fc)
                
                gemini_contents.append({"role": "model", "parts": assistant_parts})
                
                if not function_calls:
                    break
                
                # Process function calls
                tool_response_parts = []
                for fc in function_calls:
                    tool_name = fc.name
                    # Convert Map to Dict safely
                    tool_args = {}
                    if fc.args:
                        # fc.args might be a Map-like object
                        tool_args = {k: v for k, v in fc.args.items()}
                    
                    if tool_name not in tools_map:
                        tool_result = f"Error: Tool '{tool_name}' is not registered."
                    else:
                        try:
                            target_tool = tools_map[tool_name]
                            tool_result_raw = execute_tool(target_tool, tool_args)
                            if isinstance(tool_result_raw, (dict, list)):
                                tool_result = tool_result_raw # Keep as dict/list for Gemini response structure
                            else:
                                tool_result = str(tool_result_raw)
                        except Exception as te:
                            tool_result = f"Error executing tool: {str(te)}"
                            
                    executed_tools.append({
                        "name": tool_name,
                        "arguments": tool_args,
                        "result": str(tool_result)
                    })
                    
                    # Convert to proto structure if it's not raw string
                    # Gemini expects JSON/Map response format for function response
                    res_payload = tool_result if isinstance(tool_result, dict) else {"result": str(tool_result)}
                    
                    # Construct function response proto Part
                    from google.ai.generativelanguage_v1beta import Part, FunctionResponse
                    part = Part(
                        function_response=FunctionResponse(
                            name=tool_name,
                            response=res_payload
                        )
                    )
                    tool_response_parts.append(part)
                
                gemini_contents.append({
                    "role": "user",
                    "parts": tool_response_parts
                })
                
            except Exception as e:
                raise RuntimeError(f"Gemini API execution failed: {e} (at iteration {iteration})") from e
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
        
        return AdapterResponse(
            content=final_content,
            raw_response=last_response_dump,
            usage=usage_dict,
            model=target_model,
            latency_sec=total_latency,
            cost_usd=total_cost,
            tool_calls=executed_tools
        )

    async def execute_stream(
        self,
        messages: List[PromptMessage],
        model: Optional[str] = None,
        options: Optional[ExecuteOptions] = None
    ) -> AsyncIterator[StreamChunk]:
        target_model = model or "gemini-1.5-pro"
        
        system_content = ""
        gemini_contents = []
        
        for msg in messages:
            if msg.role == "system":
                system_content += msg.content + "\n"
            else:
                role = "model" if msg.role == "assistant" else "user"
                gemini_contents.append({"role": role, "parts": [msg.content]})
                
        system_content = system_content.strip()

        generation_kwargs = {}
        if options:
            generation_kwargs["temperature"] = options.temperature
            if options.max_tokens is not None:
                generation_kwargs["max_output_tokens"] = options.max_tokens
            if options.json_mode:
                generation_kwargs["response_mime_type"] = "application/json"
        else:
            generation_kwargs["temperature"] = 0.7

        generation_config = GenerationConfig(**generation_kwargs)

        model_kwargs = {}
        if system_content:
            model_kwargs["system_instruction"] = system_content

        gen_model = genai.GenerativeModel(
            model_name=target_model,
            generation_config=generation_config,
            **model_kwargs
        )

        try:
            response_stream = await gen_model.generate_content_async(
                contents=gemini_contents,
                stream=True
            )
            
            async for chunk in response_stream:
                content_piece = chunk.text if hasattr(chunk, "text") else ""
                
                # Check for usage metadata
                usage_dict = None
                if hasattr(chunk, "usage_metadata") and chunk.usage_metadata:
                    usage_dict = {
                        "prompt_tokens": chunk.usage_metadata.prompt_token_count,
                        "completion_tokens": chunk.usage_metadata.candidates_token_count,
                        "total_tokens": chunk.usage_metadata.prompt_token_count + chunk.usage_metadata.candidates_token_count
                    }
                
                # Normally the last chunk of response_stream will contain usage_metadata
                yield StreamChunk(
                    content=content_piece,
                    is_final=False,
                    usage=usage_dict
                )
            
            # Send final empty chunk to confirm termination
            yield StreamChunk(
                content="",
                is_final=True,
                usage=None
            )
            
        except Exception as e:
            raise RuntimeError(f"Gemini streaming failed: {e}") from e
