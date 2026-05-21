from typing import Protocol, runtime_checkable, Any, Dict, List, Optional, Callable, AsyncIterator
from pydantic import BaseModel

class PromptMessage(BaseModel):
    role: str
    content: str

class Tool(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
    func: Callable[..., Any]

    model_config = {
        "arbitrary_types_allowed": True
    }

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
    tool_calls: Optional[List[Dict[str, Any]]] = None


class StreamChunk(BaseModel):
    content: str
    is_final: bool = False
    usage: Optional[Dict[str, int]] = None


@runtime_checkable
class AIAdapter(Protocol):
    async def execute(
        self, 
        messages: List[PromptMessage], 
        model: Optional[str] = None,
        options: Optional[ExecuteOptions] = None
    ) -> AdapterResponse:
        ...

    async def execute_stream(
        self,
        messages: List[PromptMessage],
        model: Optional[str] = None,
        options: Optional[ExecuteOptions] = None
    ) -> AsyncIterator[StreamChunk]:
        ...
