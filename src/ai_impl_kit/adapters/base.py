from typing import Protocol, runtime_checkable, Any, Dict, List, Optional
from pydantic import BaseModel

class PromptMessage(BaseModel):
    role: str
    content: str

class ExecuteOptions(BaseModel):
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    json_mode: bool = False
    tools: Optional[List[Any]] = None


class AdapterResponse(BaseModel):
    content: str
    raw_response: Any
    usage: Dict[str, int]
    model: str
    latency_sec: float = 0.0
    cost_usd: float = 0.0

@runtime_checkable
class AIAdapter(Protocol):
    async def execute(
        self, 
        messages: List[PromptMessage], 
        model: Optional[str] = None,
        options: Optional[ExecuteOptions] = None
    ) -> AdapterResponse:
        ...
