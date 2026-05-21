import inspect
import asyncio
from typing import Dict, Any, Callable, Optional
from abc import ABC, abstractmethod

class AgentTool(ABC):
    """
    에이전트가 호출할 수 있는 도구의 기본 추상 클래스.
    """
    def __init__(self, name: str, description: str, parameters: Dict[str, Any]):
        self.name = name
        self.description = description
        self.parameters = parameters  # JSON Schema 규격

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """
        도구를 비동기적으로 실행하고 결과를 반환합니다.
        """
        pass

class FunctionTool(AgentTool):
    """
    일반 파이썬 함수를 래핑한 AgentTool 구현체.
    """
    def __init__(self, func: Callable, name: Optional[str] = None, description: Optional[str] = None):
        self.func = func
        name = name or func.__name__
        description = description or func.__doc__ or f"Tool created from function {name}"
        parameters = self._generate_schema(func)
        super().__init__(name, description, parameters)

    def _generate_schema(self, func: Callable) -> Dict[str, Any]:
        """
        인스펙션을 활용하여 함수의 Signature를 기반으로 단순 JSON Schema를 생성합니다.
        """
        sig = inspect.signature(func)
        properties = {}
        required = []

        type_map = {
            int: "integer",
            float: "number",
            str: "string",
            bool: "boolean",
            list: "array",
            dict: "object"
        }

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue
            
            p_type = param.annotation
            json_type = type_map.get(p_type, "string")
            
            properties[param_name] = {
                "type": json_type,
                "description": f"Parameter '{param_name}'"
            }
            
            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        return {
            "type": "object",
            "properties": properties,
            "required": required
        }

    async def execute(self, **kwargs) -> Any:
        if asyncio.iscoroutinefunction(self.func):
            return await self.func(**kwargs)
        else:
            # 동기 함수인 경우 스레드풀에서 실행하여 이벤트 루프 블로킹 방지
            return await asyncio.to_thread(self.func, **kwargs)

def tool(_func: Optional[Callable] = None, *, name: Optional[str] = None, description: Optional[str] = None):
    """
    일반 파이썬 함수를 AgentTool로 변환하는 데코레이터.
    괄호가 있는 경우(@tool(name="foo"))와 괄호가 없는 경우(@tool) 둘 다 지원합니다.
    """
    def decorator(func: Callable) -> FunctionTool:
        return FunctionTool(func, name=name, description=description)
        
    if _func is None:
        return decorator
    else:
        return decorator(_func)
