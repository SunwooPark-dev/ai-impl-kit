from typing import Dict, Any, Optional
import time

from ai_impl_kit.adapters.base import AIAdapter, ExecuteOptions
from ai_impl_kit.prompts.loader import PromptLoader
from ai_impl_kit.prompts.registry import registry
from ai_impl_kit.runtime.validator import ContractValidator

class PipelineExecutionResult:
    def __init__(
        self, 
        raw_output: str, 
        parsed_output: Any, 
        duration_ms: float, 
        usage: Dict[str, int],
        latency_sec: float = 0.0,
        cost_usd: float = 0.0
    ):
        self.raw_output = raw_output
        self.parsed_output = parsed_output
        self.duration_ms = duration_ms
        self.usage = usage
        self.latency_sec = latency_sec
        self.cost_usd = cost_usd

class Pipeline:
    def __init__(self, templates_dir: str, adapter: AIAdapter):
        self.loader = PromptLoader(templates_dir)
        self.adapter = adapter

    async def execute(self, prompt_id: str, inputs: Dict[str, Any], options: Optional[ExecuteOptions] = None) -> PipelineExecutionResult:
        """
        Executes the linear lifecycle of an AI feature request:
        1. Render prompt templates.
        2. Execute adapter.
        3. Validate against Output Contract.
        Fail-Fast: Any failure raises an exception immediately.
        """
        start_time = time.time()
        
        # 1. Render Prompt
        messages = self.loader.load_and_render(prompt_id, inputs)
        
        # 2. Execute Adapter
        adapter_response = await self.adapter.execute(messages=messages, options=options)
        
        # 3. Validate Output Contract
        metadata = registry.get(prompt_id)
        assert metadata is not None, f"Prompt metadata for {prompt_id} is missing."
        
        parsed_output = ContractValidator.validate(adapter_response.content, metadata.output_contract)
        
        duration_ms = (time.time() - start_time) * 1000
        
        return PipelineExecutionResult(
            raw_output=adapter_response.content,
            parsed_output=parsed_output,
            duration_ms=duration_ms,
            usage=adapter_response.usage,
            latency_sec=adapter_response.latency_sec,
            cost_usd=adapter_response.cost_usd
        )
