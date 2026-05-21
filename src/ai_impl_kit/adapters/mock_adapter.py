from typing import List, Optional
from .base import AIAdapter, PromptMessage, AdapterResponse, ExecuteOptions

class MockAdapter(AIAdapter):
    def __init__(self, response_text: Optional[str] = None):
        self.response_text = response_text

    async def execute(
        self, 
        messages: List[PromptMessage], 
        model: Optional[str] = None,
        options: Optional[ExecuteOptions] = None
    ) -> AdapterResponse:
        content = self.response_text
        if content is None:
            user_msg = next((m.content for m in messages if m.role == "user"), "")
            # Smarter routing for different prompt contracts
            if "categorize" in user_msg.lower() or "json" in user_msg.lower():
                content = '{"category": "bug", "confidence": 1.0}'
            elif "implementation" in user_msg.lower() or "task" in user_msg.lower():
                content = "# Goal\nMock Goal\n# Scope\nMock Scope\n# Implementation Plan\nPlan\n# Verification Strategy\nVerify"
            else:
                content = "# Summary\nMock Summary\n# Key Points\n- Point 1"

        return AdapterResponse(
            content=content,
            raw_response={"mock": True},
            usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            model=model or "mock-model",
            latency_sec=0.0,
            cost_usd=0.0
        )

    async def execute_stream(
        self,
        messages: List[PromptMessage],
        model: Optional[str] = None,
        options: Optional[ExecuteOptions] = None
    ):
        from .base import StreamChunk
        # Get content using same routing logic
        content = self.response_text
        if content is None:
            user_msg = next((m.content for m in messages if m.role == "user"), "")
            if "categorize" in user_msg.lower() or "json" in user_msg.lower():
                content = '{"category": "bug", "confidence": 1.0}'
            elif "implementation" in user_msg.lower() or "task" in user_msg.lower():
                content = "# Goal\nMock Goal\n# Scope\nMock Scope\n# Implementation Plan\nPlan\n# Verification Strategy\nVerify"
            else:
                content = "# Summary\nMock Summary\n# Key Points\n- Point 1"

        # Split content into chunks to simulate streaming
        words = content.split(" ")
        for i, word in enumerate(words):
            chunk_text = word + (" " if i < len(words) - 1 else "")
            is_final = (i == len(words) - 1)
            yield StreamChunk(
                content=chunk_text,
                is_final=is_final,
                usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0} if is_final else None
            )

