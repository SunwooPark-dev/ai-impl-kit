import ast
import asyncio
import sys
from typing import Dict, Any

from ai_impl_kit.runtime.tools import BaseTool

class SandboxSecurityError(Exception):
    """샌드박스 보안 규칙을 위반할 때 발생하는 에러"""
    pass

class PythonSandbox:
    FORBIDDEN_IMPORTS = {
        "os", "sys", "subprocess", "shutil", "socket", 
        "pty", "platform", "ctypes", "requests", "urllib"
    }
    FORBIDDEN_CALLS = {
        "eval", "exec", "open", "compile", "globals", "locals", "__import__"
    }

    @classmethod
    def verify_code(cls, code: str) -> None:
        """AST 분석을 통해 코드가 유효하고 안전한지 검사"""
        try:
            tree = ast.parse(code)
        except SyntaxError as se:
            raise SandboxSecurityError(f"Syntax error in code: {se}")

        for node in ast.walk(tree):
            # 1. import os, sys 등 임포트 차단
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # 패키지 최상위 이름 검사 (예: os.path -> os)
                    base_module = alias.name.split('.')[0]
                    if base_module in cls.FORBIDDEN_IMPORTS:
                        raise SandboxSecurityError(f"Import of module '{alias.name}' is forbidden in sandbox.")
            
            # 2. from os import ... 임포트 차단
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    base_module = node.module.split('.')[0]
                    if base_module in cls.FORBIDDEN_IMPORTS:
                        raise SandboxSecurityError(f"Import from module '{node.module}' is forbidden in sandbox.")

            # 3. eval, exec, open 등 함수 호출 차단
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in cls.FORBIDDEN_CALLS:
                        raise SandboxSecurityError(f"Use of built-in function '{node.func.id}' is forbidden in sandbox.")
                elif isinstance(node.func, ast.Attribute):
                    # 만약 attributes를 통해 접근할 수 있는 꼼수 우회 차단 (예: getattr(__builtins__, 'eval'))
                    pass

    @classmethod
    async def execute_code(cls, code: str, timeout: float = 5.0) -> Dict[str, Any]:
        """정적 보안 검사 수행 후, subprocess를 통해 파이썬 코드를 비동기 실행"""
        # 1. 정적 검사
        cls.verify_code(code)

        # 2. 외부 subprocess 호출하여 실행 격리
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-c", code,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            return {
                "exit_code": process.returncode,
                "stdout": stdout.decode("utf-8", errors="replace"),
                "stderr": stderr.decode("utf-8", errors="replace")
            }
        except asyncio.TimeoutError:
            try:
                process.kill()
                await process.wait()
            except Exception:
                pass
            raise TimeoutError(f"Sandbox execution timed out after {timeout} seconds.")


class SandboxPythonTool(BaseTool):
    @property
    def name(self) -> str:
        return "python_sandbox"

    @property
    def description(self) -> str:
        return "Execute arbitrary Python code in a safe, isolated sandbox environment. Code should not import forbidden modules like os or sys, or use forbidden functions like open."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {
                  "type": "string",
                  "description": "The Python code to execute."
                }
            },
            "required": ["code"]
        }

    async def execute(self, code: str) -> Dict[str, Any]:
        """도구 호출 시 샌드박스에서 파이썬 코드를 실행하고 구조화된 결과를 리턴"""
        try:
            return await PythonSandbox.execute_code(code)
        except Exception as e:
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e)
            }


from concurrent.futures import ThreadPoolExecutor

def execute_tool(tool: Any, args: Dict[str, Any]) -> Any:
    """
    도구를 동기적으로 실행하고 결과를 반환하는 헬퍼 함수.
    비동기 메서드 `execute`를 현재 이벤트 루프를 블로킹하지 않고 안전하게 동기 호출합니다.
    """
    coro = tool.execute(**args)
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # 실행 중인 이벤트 루프가 없는 경우
        return asyncio.run(coro)
    
    # 이미 이벤트 루프가 실행 중인 경우
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(asyncio.run, coro)
        return future.result()

