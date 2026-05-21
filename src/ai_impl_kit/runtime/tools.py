from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """도구 이름"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """도구 설명"""
        pass

    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """도구 호출에 필요한 JSON Schema 파라미터 정의"""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """도구 비동기 실행 로직"""
        pass
